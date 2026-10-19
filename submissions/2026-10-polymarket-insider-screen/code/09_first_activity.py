"""Look up when every tested wallet first appeared on Polymarket (Data API /activity, oldest first).

Deposits and withdrawals count as activity, so a wallet funded days before its first trade is not
taken for a new one. All tested wallets are looked up, so the fresh signal is known for every row
of the ranking and the share of fresh wallets among all tested wallets is the baseline the review
list is compared with. The lookup resumes from the output file if it is interrupted.
"""
import os
import sys
import time

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
GZ = {"method": "gzip", "mtime": 0}


def first_activity(wallet):
    params = {"user": wallet, "limit": 1, "sortDirection": "ASC", "excludeDepositsWithdrawals": "false"}
    for attempt in range(8):
        try:
            r = S.get("https://data-api.polymarket.com/activity", params=params, timeout=60)
            if r.status_code == 200:
                rows = r.json()
                return rows[0]["timestamp"] if rows else None
        except requests.RequestException:
            pass
        time.sleep(min(2 ** attempt, 60))
    raise RuntimeError(f"activity lookup failed for {wallet}")


def main(datadir, out):
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    look = wallets.loc[wallets["status"] == "tested", "wallet"].tolist()
    done = pd.read_csv(out) if os.path.exists(out) else pd.DataFrame(columns=["wallet", "first_activity_ts"])
    have = set(done["wallet"])
    rows = done.to_dict("records")
    todo = [w for w in look if w not in have]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for i, (wallet, ts) in enumerate(zip(todo, pool.map(first_activity, todo))):
            rows.append({"wallet": wallet, "first_activity_ts": ts})
            if i % 500 == 0:
                pd.DataFrame(rows).to_csv(out, index=False, compression=GZ)
                print(i, flush=True)
    t = pd.DataFrame(rows)
    t = t[t["wallet"].isin(set(look))].sort_values("wallet")
    t["first_activity_ts"] = t["first_activity_ts"].astype("Int64")
    t.to_csv(out, index=False, compression=GZ)


if __name__ == "__main__":
    main(*sys.argv[1:3])
