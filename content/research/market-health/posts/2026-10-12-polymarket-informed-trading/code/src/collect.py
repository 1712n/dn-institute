import json
import time
import threading
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed

import duckdb
import pandas as pd

import config
from src.pm_client import PolymarketClient


def _f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def _parse_market(m, apply_band=True):
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except (ValueError, TypeError):
        return None
    if len(outcomes) != 2 or len(prices) != 2:
        return None
    decisive = max(prices) >= 0.99 and min(prices) <= 0.01
    if not decisive:
        return None
    win_index = 0 if prices[0] > prices[1] else 1
    vol = _f(m.get("volumeNum"))
    if apply_band and not (config.MIN_MARKET_VOLUME <= vol <= config.MAX_MARKET_VOLUME):
        return None
    return {
        "condition_id": m.get("conditionId"),
        "slug": m.get("slug"),
        "question": m.get("question"),
        "event_slug": (m.get("events") or [{}])[0].get("slug") if m.get("events") else None,
        "start_date": m.get("startDate"),
        "end_date": m.get("endDate"),
        "volume": vol,
        "outcomes": json.dumps(outcomes),
        "win_index": win_index,
        "win_outcome": outcomes[win_index],
        "token_win": tokens[win_index] if len(tokens) == 2 else None,
        "token_lose": tokens[1 - win_index] if len(tokens) == 2 else None,
        "resolved_by": m.get("resolvedBy"),
    }


def fetch_markets(client):
    rows, offset = [], 0
    while True:
        page = client.markets_page(config.POLITICS_TAG_ID, offset, limit=100,
                                   end_min=config.WINDOW_START, end_max=config.WINDOW_END)
        if not page:
            break
        for m in page:
            p = _parse_market(m)
            if p and p["condition_id"]:
                rows.append(p)
        offset += len(page)
        if len(page) < 100 or len(rows) >= config.MAX_MARKETS:
            break
    df = pd.DataFrame(rows).drop_duplicates("condition_id")
    df = df.sort_values("volume", ascending=False).head(config.MAX_MARKETS).reset_index(drop=True)
    return df


def fetch_trades(client, condition_id):
    out, offset = [], 0
    while offset < config.TRADES_OFFSET_CAP:
        page = client.trades_page(condition_id, offset)
        if not page:
            break
        for t in page:
            if t.get("outcomeIndex") is None:
                continue  # side unknown: counting it on outcome 0 would misprice the winner
            out.append({
                "condition_id": condition_id,
                "wallet": t.get("proxyWallet"),
                "side": t.get("side"),
                "size": _f(t.get("size")),
                "price": _f(t.get("price")),
                "timestamp": int(t.get("timestamp") or 0),
                "outcome_index": int(t["outcomeIndex"]),
                "tx_hash": t.get("transactionHash"),
                "pseudonym": t.get("pseudonym"),
                "name": t.get("name"),
                "bio": t.get("bio"),
            })
        offset += len(page)
        if len(page) < config.TRADES_PAGE:
            break
    return pd.DataFrame(out), offset >= config.TRADES_OFFSET_CAP


def run(db_path=None, verbose=True):
    db_path = str(db_path or config.DB_PATH)
    config.DATA_DIR.mkdir(exist_ok=True)
    client = PolymarketClient()
    con = duckdb.connect(db_path)
    con.execute("DROP TABLE IF EXISTS markets")
    con.execute("DROP TABLE IF EXISTS trades")

    markets = fetch_markets(client)
    markets["trades_capped"] = False
    if verbose:
        print(f"[markets] selected {len(markets)} politics markets in window")

    all_trades = []
    for i, row in markets.iterrows():
        tdf, capped = fetch_trades(client, row["condition_id"])
        markets.at[i, "trades_capped"] = capped
        if len(tdf):
            all_trades.append(tdf)
        if verbose:
            print(f"[trades] {i + 1}/{len(markets)} {row['slug'][:48]:50s} "
                  f"n={len(tdf):6d}{' CAP' if capped else ''}")

    con.execute("DROP TABLE IF EXISTS markets")
    con.register("markets_df", markets)
    con.execute("CREATE TABLE markets AS SELECT * FROM markets_df")

    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    con.register("trades_df", trades)
    con.execute("CREATE TABLE trades AS SELECT * FROM trades_df")
    if verbose:
        print(f"[done] markets={len(markets)} trades={len(trades)} wallets={trades['wallet'].nunique() if len(trades) else 0}")
    con.close()
    return markets, trades


def _slices(start, end, days):
    a = dt.datetime.fromisoformat(start.replace("Z", "+00:00"))
    b = dt.datetime.fromisoformat(end.replace("Z", "+00:00"))
    cur = a
    while cur < b:
        nxt = min(cur + dt.timedelta(days=days), b)
        yield cur.strftime("%Y-%m-%dT%H:%M:%SZ"), nxt.strftime("%Y-%m-%dT%H:%M:%SZ")
        cur = nxt


def fetch_all_markets(client, days=7):
    seen = {}
    for lo, hi in _slices(config.WINDOW_START, config.WINDOW_END, days):
        offset = 0
        while True:
            page = client.markets_page(config.POLITICS_TAG_ID, offset, limit=100,
                                       end_min=lo, end_max=hi)
            if not page:
                break
            for m in page:
                p = _parse_market(m, apply_band=False)
                if p and p["condition_id"] and p["condition_id"] not in seen:
                    seen[p["condition_id"]] = p
            offset += len(page)
            if len(page) < 100:
                break
            if offset >= 2000:
                break
    df = pd.DataFrame(list(seen.values()))
    return df.sort_values("volume", ascending=False).reset_index(drop=True)


_TRADES_DDL = """CREATE TABLE IF NOT EXISTS trades(
    condition_id VARCHAR, wallet VARCHAR, side VARCHAR, size DOUBLE, price DOUBLE,
    timestamp BIGINT, outcome_index INTEGER, tx_hash VARCHAR,
    pseudonym VARCHAR, name VARCHAR, bio VARCHAR)"""


def run_full(db_path=None, min_volume=1.0, verbose=True):
    db_path = str(db_path or config.DB_PATH)
    config.DATA_DIR.mkdir(exist_ok=True)
    client = PolymarketClient()
    con = duckdb.connect(db_path)

    has_u = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name='universe'").fetchone()[0]
    if not has_u:
        markets = fetch_all_markets(client)
        con.register("mdf", markets)
        con.execute("CREATE TABLE universe AS SELECT * FROM mdf")
        if verbose:
            print(f"[universe] {len(markets)} binary politics markets in window", flush=True)
    con.execute(_TRADES_DDL)
    con.execute("CREATE TABLE IF NOT EXISTS collected(condition_id VARCHAR, n_trades INTEGER, capped BOOLEAN)")

    targets = con.execute(f"""
        SELECT condition_id, slug, volume FROM universe
        WHERE volume >= {min_volume}
          AND condition_id NOT IN (SELECT condition_id FROM collected)
        ORDER BY volume DESC""").df()
    done = con.execute("SELECT count(*) FROM collected").fetchone()[0]
    total = len(targets) + done
    if verbose:
        print(f"[plan] {len(targets)} markets to collect (already done {done}, total {total})", flush=True)

    tcount = 0
    for i, row in targets.iterrows():
        cid = row["condition_id"]
        tdf, capped = fetch_trades(client, cid)
        _store(con, cid, tdf, capped)
        tcount += len(tdf)
        if verbose and (i % 25 == 0 or len(tdf) >= 5000):
            print(f"[{done + i + 1}/{total}] vol={int(row['volume']):>9} n={len(tdf):6d}"
                  f"{' CAP' if capped else ''}  {str(row['slug'])[:46]}", flush=True)

    con.execute("""CREATE OR REPLACE TABLE markets AS
        SELECT u.*, c.n_trades, COALESCE(c.capped, false) AS trades_capped
        FROM universe u LEFT JOIN collected c USING (condition_id)""")
    nt = con.execute("SELECT count(*) FROM trades").fetchone()[0]
    nw = con.execute("SELECT count(DISTINCT wallet) FROM trades").fetchone()[0]
    if verbose:
        print(f"[done] trades={nt:,} wallets={nw:,}", flush=True)
    con.close()
    return nt, nw


def _store(con, cid, tdf, capped):
    """Write one market's trades and its `collected` row together, or neither."""
    con.execute("BEGIN")
    try:
        if len(tdf):
            con.register("tmp", tdf)
            con.execute("INSERT INTO trades SELECT * FROM tmp")
            con.unregister("tmp")
        con.execute("INSERT INTO collected VALUES (?,?,?)", [cid, int(len(tdf)), bool(capped)])
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise


_tl = threading.local()


def _client():
    if not hasattr(_tl, "c"):
        _tl.c = PolymarketClient()
    return _tl.c


def run_full_parallel(db_path=None, min_volume=1.0, workers=16, verbose=True):
    db_path = str(db_path or config.DB_PATH)
    config.DATA_DIR.mkdir(exist_ok=True)
    config.REQUEST_PAUSE = 0.05
    con = duckdb.connect(db_path)

    has_u = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name='universe'").fetchone()[0]
    if not has_u:
        markets = fetch_all_markets(_client())
        con.register("mdf", markets)
        con.execute("CREATE TABLE universe AS SELECT * FROM mdf")
        if verbose:
            print(f"[universe] {len(markets)} binary politics markets in window", flush=True)
    con.execute(_TRADES_DDL)
    con.execute("CREATE TABLE IF NOT EXISTS collected(condition_id VARCHAR, n_trades INTEGER, capped BOOLEAN)")

    targets = con.execute(f"""
        SELECT condition_id, volume FROM universe
        WHERE volume >= {min_volume}
          AND condition_id NOT IN (SELECT condition_id FROM collected)
        ORDER BY volume DESC""").df()
    done0 = con.execute("SELECT count(*) FROM collected").fetchone()[0]
    total = len(targets) + done0
    if verbose:
        print(f"[plan] {len(targets)} markets to collect (done {done0}, total {total}, workers {workers})", flush=True)

    def work(cid):
        tdf, capped = fetch_trades(_client(), cid)
        return cid, tdf, capped

    t0 = time.time()
    done = done0
    tcount = 0
    failed = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(work, c): c for c in targets["condition_id"]}
        for fut in as_completed(futs):
            try:
                cid, tdf, capped = fut.result()
            except Exception as e:
                # not marked collected, so the next run retries it
                failed.append(futs[fut])
                if verbose:
                    print(f"[failed] {futs[fut]}: {e}", flush=True)
                continue
            _store(con, cid, tdf, capped)
            done += 1
            tcount += len(tdf)
            if verbose and done % 100 == 0:
                el = time.time() - t0
                rate = (done - done0) / el if el else 0
                eta = (total - done) / rate / 60 if rate else 0
                print(f"[{done}/{total}] trades+={tcount:,} {rate:.1f} mkt/s eta {eta:.0f}m", flush=True)

    con.execute("""CREATE OR REPLACE TABLE markets AS
        SELECT u.*, c.n_trades, COALESCE(c.capped, false) AS trades_capped
        FROM universe u LEFT JOIN collected c USING (condition_id)""")
    nt = con.execute("SELECT count(*) FROM trades").fetchone()[0]
    nw = con.execute("SELECT count(DISTINCT wallet) FROM trades").fetchone()[0]
    if verbose:
        print(f"[done] markets_collected={done} trades={nt:,} wallets={nw:,} in {(time.time()-t0)/60:.1f}m", flush=True)
        if failed:
            print(f"[retry] {len(failed)} markets failed; run again to collect them", flush=True)
    con.close()
    return nt, nw
