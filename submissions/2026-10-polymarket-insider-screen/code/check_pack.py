"""Check the committed data against the rules of 02_window.py and 05_pack.py, from committed files only.

  window    every screened market has LO <= closedTime < HI.
  clocks    closed_ts, end_cap and deadline_ts recomputed with the functions of 05_pack.py,
            t_settle recomputed from market_buckets.csv.xz, and t_known and t_known_source
            equal to the earliest clock.
  tape      every committed trade is on or after LO, before its market's t_known and belongs
            to a tested wallet, and the trade count per market equals n_trades_committed.
  wallets   every status in wallets.csv.gz recomputed: tested wallets from the tape, the
            others from wallets_excluded_markets.csv.gz.
  checksums every file in SHA256SUMS matches, and every data file is listed.

Prints one line per check and exits 1 if any fails. Usage: python code/check_pack.py data
"""
import glob
import hashlib
import importlib.util
import os
import sys

import numpy as np
import pandas as pd


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


window, pack, features = load("02_window"), load("05_pack"), load("06_features")


def same(a, b, tol=1e-6):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(np.all((np.isnan(a) & np.isnan(b)) | (np.abs(a - b) <= tol)))


def main(datadir):
    ok = {}
    m = pd.read_csv(os.path.join(datadir, "markets_scope.csv"), dtype={"id": str, "event_id": str})
    closed = pd.to_datetime(m["closedTime"], utc=True, format="mixed")
    before, after = int((closed < window.LO).sum()), int((closed >= window.HI).sum())
    print(f"window: {len(m)} markets, {before} closed before {window.LO.date()}, {after} on or after {window.HI.date()}")
    ok["window"] = before == 0 and after == 0

    c = pack.clocks(m.drop(columns=["closed_ts", "end_ts", "deadline_ts", "end_cap"]))
    bk = pd.read_csv(os.path.join(datadir, "market_buckets.csv.xz"))
    ts = bk[bk["yes_vwap"] >= pack.SETTLED].groupby("m")["b"].min().reindex(m["m"]).to_numpy(dtype=float)
    known = [pack.known(r, t) for (_, r), t in zip(c.iterrows(), ts)]
    checks = {"closed_ts": same(c["closed_ts"], m["closed_ts"]), "end_cap": same(c["end_cap"], m["end_cap"]),
              "deadline_ts": same(c["deadline_ts"], m["deadline_ts"]), "t_settle": same(ts, m["t_settle"]),
              "t_known": same([k[0] for k in known], m["t_known"]),
              "t_known_source": [k[1] for k in known] == m["t_known_source"].tolist()}
    print("clocks:", ", ".join(f"{k} {'ok' if v else 'DIFFERS'}" for k, v in checks.items()))
    ok["clocks"] = all(checks.values())

    w = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    tested = w[(w["status"] == "tested") & w["w"].notna()]
    t = features.read_tape(datadir).merge(m[["m", "t_known"]], on="m", how="left")
    late = int((t["ts"] >= t["t_known"]).sum())
    early = int((t["ts"] < window.LO.timestamp()).sum())
    stray = int((~t["w"].isin(tested["w"].astype(int))).sum())
    per_m = t.groupby("m").size().reindex(m["m"], fill_value=0).to_numpy()
    bad_n = int((per_m != m["n_trades_committed"].to_numpy()).sum())
    print(f"tape: {len(t)} trades, {early} before {window.LO.date()}, {late} at or after t_known, "
          f"{stray} from untested wallets, {bad_n} markets whose count differs")
    ok["tape"] = early == 0 and late == 0 and stray == 0 and bad_n == 0

    op = features.read_opening(datadir)
    if op is not None:
        on_tape = set(zip(t["w"], t["m"]))
        off = sum((w_, m_) not in on_tape for w_, m_ in zip(op["w"], op["m"]))
        made = set(m.loc[pd.to_datetime(m["createdAt"], utc=True, format="mixed") >= window.LO, "m"])
        new = int(op["m"].isin(made).sum())
        neg = int(((op["open_0"] < 0) | (op["open_1"] < 0) | (op["open_cost"] < 0)).sum())
        print(f"opening positions: {len(op)}, {off} not on the tape, {new} in markets created in the window, {neg} negative")
        ok["opening"] = off == 0 and neg == 0

    t["usd"] = np.where(t["side"] == "B", t["size"] * t["price"], 0.0)
    pm = t.pivot_table(index=["w", "m"], columns="o", values="usd", aggfunc="sum", fill_value=0.0)
    pm["n"] = t.groupby(["w", "m"]).size()
    pm = pm.reset_index().rename(columns={0: "buy_usd_0", 1: "buy_usd_1", "n": "n_trades"})
    pm["wallet"] = pm["w"].map(tested.set_index(tested["w"].astype(int))["wallet"])
    ex = pd.read_csv(os.path.join(datadir, "wallets_excluded_markets.csv.gz"))
    rows = pd.concat([pm[["wallet", "m", "n_trades", "buy_usd_0", "buy_usd_1"]], ex], ignore_index=True)
    tot = rows["buy_usd_0"] + rows["buy_usd_1"]
    rows["ratio"] = np.where(tot > 0, 2 * np.minimum(rows["buy_usd_0"], rows["buy_usd_1"]) / tot.where(tot > 0, 1.0), np.nan)
    g = rows.groupby("wallet")
    re = pd.DataFrame({"buy": g["buy_usd_0"].sum() + g["buy_usd_1"].sum(), "n": g["n_trades"].sum(),
                       "two": g["ratio"].mean()}).reindex(w["wallet"])
    status = np.where(re["two"] > pack.MM_RATIO, "market_maker",
                      np.where(re["n"] > pack.MAX_TRADES, "high_frequency", "tested"))
    wchecks = {"buy_usd_pre_known": same(re["buy"], w["buy_usd_pre_known"], 0.01),
               "n_trades_pre_known": same(re["n"], w["n_trades_pre_known"]),
               "two_sided_mean": same(re["two"], w["two_sided_mean"], 1e-5),
               "status": (status == w["status"].to_numpy()).all(),
               "floor": bool((re["buy"] >= pack.WALLET_FLOOR - 0.01).all())}
    print(f"wallets: {len(w)} over the floor,", ", ".join(f"{k} {'ok' if v else 'DIFFERS'}" for k, v in wchecks.items()))
    ok["wallets"] = all(wchecks.values())

    sums, path = {}, os.path.join(datadir, "SHA256SUMS")
    for line in open(path) if os.path.exists(path) else []:
        h, name = line.split()
        sums[name] = h
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(datadir, "*")) if not p.endswith("SHA256SUMS"))
    unlisted = [f for f in files if f not in sums and f != "wallet_market.csv.gz"]
    wrong = [n for n, h in sums.items() if hashlib.sha256(open(os.path.join(datadir, n), "rb").read()).hexdigest() != h]
    print(f"checksums: {len(sums)} listed, {len(wrong)} differ, {len(unlisted)} files unlisted", *(wrong + unlisted))
    ok["checksums"] = not wrong and not unlisted

    print("all checks pass" if all(ok.values()) else "FAILED: " + ", ".join(k for k, v in ok.items() if not v))
    sys.exit(0 if all(ok.values()) else 1)


if __name__ == "__main__":
    main(sys.argv[1])
