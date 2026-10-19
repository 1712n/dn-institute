"""Check every named account whose address came from a profile name (needs network).

For rows of known_cases.csv identified by "profile name in source", Gamma's public-profile endpoint
must return that name, as the display name or as the generated pseudonym, for the committed
address. Exits 1 if any row fails. Usage: python code/check_known_cases.py data
"""
import os
import sys

import pandas as pd
import requests


def main(datadir):
    k = pd.read_csv(os.path.join(datadir, "known_cases.csv")).fillna("")
    bad = 0
    for _, row in k[k["how_identified"] == "profile name in source"].iterrows():
        r = requests.get("https://gamma-api.polymarket.com/public-profile", headers={"User-Agent": "Mozilla/5.0"},
                         params={"address": row["address"]}, timeout=60)
        r.raise_for_status()
        names = {r.json().get("name"), r.json().get("pseudonym")}
        ok = row["profile_name"] in names
        bad += not ok
        print("ok " if ok else "BAD", row["address"], row["profile_name"], sorted(n for n in names if n))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1])
