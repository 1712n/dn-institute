import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import pandas as pd

import config
from src import collect, features, scoring, osint
from src.pm_client import PolymarketClient


def _load_cached():
    con = duckdb.connect(str(config.DB_PATH))
    m = con.execute("SELECT * FROM markets").df()
    t = con.execute("SELECT * FROM trades").df()
    con.close()
    return m, t


def main():
    cached = "--cached" in sys.argv
    if cached and config.DB_PATH.exists():
        print("[stage] loading cached collection")
        markets, trades = _load_cached()
    else:
        print("[stage] collecting from Polymarket")
        markets, trades = collect.run()

    if not len(trades):
        print("no trades collected; aborting")
        return

    print("[stage] building features")
    wm = features.build(markets, trades)

    print("[stage] scoring")
    W = scoring.aggregate(wm, trades)
    ranked = scoring.score(W)
    rk, flg, msum = scoring.write_outputs(markets, trades, wm, W, ranked)

    print("[stage] OSINT enrichment (top candidates)")
    client = PolymarketClient()
    dossier = osint.enrich_top(ranked, client, top_n=25)
    dossier.to_csv(config.OUTPUT_DIR / "osint_dossier.csv", index=False)

    print("\n==== SUMMARY ====")
    print(f"markets analysed : {len(markets)}")
    print(f"trades analysed  : {len(trades):,}")
    print(f"wallets observed : {trades['wallet'].nunique():,}")
    print(f"wallets ranked   : {len(ranked):,}")
    print(f"flagged (w,market): {int(wm['flag'].sum()):,}")
    print("\nTop 15 by Insider Likelihood Score:")
    show = ranked.head(15)[["rank", "wallet", "pseudonym", "ILS", "n_flagged",
                            "hit_rate", "realized_pnl", "vwap_entry_w", "fwd_move_w"]]
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(show.to_string(index=False))
    print("\noutputs -> output/*.csv")


if __name__ == "__main__":
    main()
