import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

import config
from src.pm_client import PolymarketClient
from src import osint

LIFETIME_CACHE = config.INPUT_DIR / "lifetime_profiles.csv"
FIRST_ACTIVITY_CACHE = config.INPUT_DIR / "wallet_first_activity.csv"

_tl = threading.local()


def _client():
    if not hasattr(_tl, "c"):
        _tl.c = PolymarketClient()
    return _tl.c


def fetch_lifetime_parallel(wallets, workers=16):
    def work(w):
        try:
            lt = osint._lifetime(_client(), w)
        except Exception:
            return None
        return {"wallet": w, "lt_markets": lt["lt_markets"], "lt_pnl": lt["lt_pnl"]}
    rows = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(work, w) for w in wallets]):
            r = fut.result()
            if r is not None:
                rows.append(r)
    return pd.DataFrame(rows, columns=["wallet", "lt_markets", "lt_pnl"])


def lifetime_profiles(wallets, offline=False, workers=16):
    """Lifetime profile per wallet, served from a snapshot so reruns are reproducible.

    Wallets missing from the snapshot are fetched from /positions and appended, unless
    `offline`; wallets that stay unknown get no row (and later M_lifetime = 1).
    """
    wallets = set(wallets)
    cols = ["wallet", "lt_markets", "lt_pnl"]
    cache = pd.read_csv(LIFETIME_CACHE) if LIFETIME_CACHE.exists() else pd.DataFrame(columns=cols)
    missing = sorted(wallets - set(cache["wallet"]))
    if missing and not offline:
        fresh = fetch_lifetime_parallel(missing, workers=workers)
        if len(fresh):
            cache = pd.concat([cache, fresh], ignore_index=True)
            cache = cache.drop_duplicates("wallet").sort_values("wallet")
            LIFETIME_CACHE.parent.mkdir(parents=True, exist_ok=True)
            cache.round({"lt_pnl": 4}).to_csv(LIFETIME_CACHE, index=False)
    return cache[cache["wallet"].isin(wallets)].reset_index(drop=True)


def _first_activity(wallet):
    act = _client().activity(wallet, limit=1, oldest_first=True)
    if act is None:
        raise RuntimeError(f"activity lookup failed for {wallet}")
    return {"wallet": wallet, "first_activity_ts": act[0]["timestamp"] if act else None}


def first_activity(wallets, offline=False, workers=8):
    """Timestamp of each wallet's first Polymarket activity, served from a snapshot like
    lifetime_profiles; wallets missing from it are fetched unless `offline`."""
    cols = ["wallet", "first_activity_ts"]
    cache = pd.read_csv(FIRST_ACTIVITY_CACHE) if FIRST_ACTIVITY_CACHE.exists() else pd.DataFrame(columns=cols)
    missing = sorted(set(wallets) - set(cache["wallet"]))
    if missing and not offline:
        rows = []
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for fut in as_completed([ex.submit(_first_activity, w) for w in missing]):
                try:
                    rows.append(fut.result())
                except Exception:
                    pass
        if rows:
            cache = pd.concat([cache, pd.DataFrame(rows, columns=cols)], ignore_index=True)
            cache.sort_values("wallet").to_csv(FIRST_ACTIVITY_CACHE, index=False)
            cache = pd.read_csv(FIRST_ACTIVITY_CACHE)
    return cache[cache["wallet"].isin(set(wallets))].reset_index(drop=True)


def lifetime_multiplier(lt_markets, lt_pnl):
    if lt_markets is None or lt_markets != lt_markets:
        return 1.0, "no_data"
    lt_markets = int(lt_markets)
    if lt_markets == 0:
        return 1.0, "no_positions"
    M, tag = 1.0, "normal"
    if lt_markets <= 10:
        M += 0.30; tag = "fresh"
    elif lt_markets <= 30:
        M += 0.15; tag = "low_footprint"
    elif lt_markets >= 300:
        M -= 0.35; tag = "very_high_activity"
    elif lt_markets >= 120:
        M -= 0.20; tag = "high_activity"
    if lt_markets >= 80 and lt_pnl <= -20000:
        M -= 0.40; tag = "degen_loser"
    elif lt_markets >= 50 and lt_pnl <= -5000:
        M -= 0.15; tag = "net_loser"
    if lt_markets <= 60 and lt_pnl > 0:
        M += 0.10
        if tag == "normal":
            tag = "clean_profitable"
    return max(0.3, min(1.4, M)), tag


def cooccurrence(ep, window_sec=900, min_shared=2, burst_sec=180, burst_n=3):
    pair_markets = defaultdict(set)
    adj = defaultdict(set)
    edges = []
    for slug, g in ep.groupby("slug"):
        arr = g[["wallet", "entry_ts"]].sort_values("entry_ts").to_numpy()
        n = len(arr)
        for i in range(n):
            burst = {arr[i][0]}
            for j in range(i + 1, n):
                dt = arr[j][1] - arr[i][1]
                if dt > window_sec:
                    break
                if arr[i][0] == arr[j][0]:
                    continue
                pair = tuple(sorted((arr[i][0], arr[j][0])))
                pair_markets[pair].add(slug)
                if dt <= burst_sec:
                    burst.add(arr[j][0])
            # intra-market synchronized burst: many distinct wallets within burst_sec
            if len(burst) >= burst_n:
                bl = sorted(burst)
                for a in bl:
                    for b in bl:
                        if a < b:
                            adj[a].add(b); adj[b].add(a)
                            edges.append((a, b, "burst:" + slug[:24]))
    for (a, b), mk in pair_markets.items():
        if len(mk) >= min_shared:
            adj[a].add(b); adj[b].add(a)
            edges.append((a, b, "xmarket:%d" % len(mk)))
    seen, clusters = set(), []
    for node in adj:
        if node in seen:
            continue
        comp, stack = set(), [node]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x); seen.add(x)
            stack.extend(adj[x] - comp)
        if len(comp) >= 2:
            clusters.append(comp)
    cid = {}
    for i, comp in enumerate(clusters):
        for w in comp:
            cid[w] = i
    return cid, clusters, edges
