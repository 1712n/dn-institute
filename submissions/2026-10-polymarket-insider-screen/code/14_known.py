"""Where the ranking puts the accounts that the press or prosecutors named.

known_cases.csv lists each named account with its source and how the address was taken: printed
in the source, in a profile link in the source, or from a profile name the source printed, which
check_known_cases.py confirms against Gamma's public-profile endpoint. The signals and weights in
10_score.py were not tuned on these accounts.

known_case_recall.csv gives each account's status and rank. The printed tail probability is the
chance that at least as many of the tested named accounts land in the top REVIEW if the ranking
put them at random (hypergeometric).
"""
import importlib.util
import math
import os
import sys

import pandas as pd

_spec = importlib.util.spec_from_file_location("scoring", os.path.join(os.path.dirname(__file__), "10_score.py"))
scoring = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scoring)


def tail(n, k, draws, hits):
    """P(X >= hits) for X hypergeometric: draws from n items of which k are marked."""
    total = math.comb(n, draws)
    return sum(math.comb(k, i) * math.comb(n - k, draws - i) for i in range(hits, min(k, draws) + 1)) / total


def main(datadir, out):
    kc = pd.read_csv(os.path.join(datadir, "known_cases.csv"))
    kc["address"] = kc["address"].str.lower()
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    rk = pd.read_csv(os.path.join(datadir, "wallet_ranking_full.csv.gz"))
    r = kc.merge(wallets[["wallet", "status"]], left_on="address", right_on="wallet", how="left").drop(columns="wallet")
    r["status"] = r["status"].fillna("under_floor")
    r = r.merge(rk[["wallet", "rank", "score", "pnl", "early_longshot_usd", "top_event"]], left_on="address",
                right_on="wallet", how="left").drop(columns="wallet")
    r["in_review_list"] = r["rank"] <= scoring.REVIEW
    r.round(4).to_csv(out, index=False)
    tested = r[r["status"] == "tested"]
    hits = int(tested["in_review_list"].sum())
    p = tail(len(rk), len(tested), scoring.REVIEW, hits)
    print(r[["case", "address", "status", "rank", "pnl", "top_event"]].to_string(index=False))
    print(len(r), "named;", len(tested), "tested;", hits, "in the top", scoring.REVIEW, "of", len(rk), "; chance by luck", f"{p:.3g}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
