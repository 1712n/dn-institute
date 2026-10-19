"""Earlier-day control: the same ranking with every outcome clock moved back.

Each market's t_known is moved SHIFTS days earlier, trades after the moved clock are dropped, and
the wallets are scored again; outcomes stay as they were. If the ranking only rewarded wallets
that are often right, the top scores would look the same on these ordinary days. control.csv
says, for each shift, how many wallets reach the score of rank REVIEW in the real ranking, and
how many of the real review list are still in the shifted one.
"""
import importlib.util
import os
import sys

import pandas as pd


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


features, scoring = load("06_features"), load("10_score")
SHIFTS = (7, 14)


def main(datadir, out):
    tape, scope = features.read_tape(datadir), features.read_scope(datadir)
    opening = features.read_opening(datadir)
    wallets = pd.read_csv(os.path.join(datadir, "wallets.csv.gz"))
    fa = pd.read_csv(os.path.join(datadir, "wallet_first_activity.csv.gz"))
    real = pd.read_csv(os.path.join(datadir, "wallet_ranking_full.csv.gz"))
    cut = real.loc[real["rank"] == scoring.REVIEW, "score"].iloc[0]
    top = set(real.loc[real["rank"] <= scoring.REVIEW, "wallet"])
    rows = [{"shift_days": 0, "wallets_ranked": len(real), "wallets_at_or_above_cut": int((real["score"] >= cut).sum()),
             "review_list_still_in_top": len(top)}]
    for d in SHIFTS:
        s = scope.copy()
        s["t_known"] = s["t_known"] - d * 86400
        r = scoring.ranking(features.wallet_market(tape, s, opening), wallets, fa, s)
        rows.append({"shift_days": d, "wallets_ranked": len(r), "wallets_at_or_above_cut": int((r["score"] >= cut).sum()),
                     "review_list_still_in_top": len(top & set(r.loc[r["rank"] <= scoring.REVIEW, "wallet"]))})
        print(rows[-1], flush=True)
    tab = pd.DataFrame(rows)
    tab.insert(1, "score_cut", round(cut, 4))
    tab.to_csv(out, index=False)
    print(tab.to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
