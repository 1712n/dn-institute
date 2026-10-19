"""Check that the backwards walk in 04_trades.py loses and repeats no trade.

Takes a market small enough to fetch with plain offsets (under 20,000 trades), fetches it once
with the normal window and once with windows of 1,000 trades, and compares the two lists as
multisets. Needs network access. Usage: python code/check_tape_walk.py <conditionId>
"""
import importlib.util
import os
import sys
from collections import Counter

_spec = importlib.util.spec_from_file_location("trades", os.path.join(os.path.dirname(__file__), "04_trades.py"))
trades = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trades)


def key(r):
    return (r["proxyWallet"], r["side"], r["asset"], r["size"], r["price"], r["timestamp"], r["transactionHash"])


def main(cid):
    full, kind, windows = trades.fetch_market(cid)
    trades.LIMIT = 1000
    small, kind_small, windows_small = trades.fetch_market(cid)
    same = Counter(map(key, full)) == Counter(map(key, small))
    print(f"default walk: {len(full)} trades in {windows} window(s), {kind}")
    print(f"1,000-trade walk: {len(small)} trades in {windows_small} window(s), {kind_small}")
    print("same trades:", same)
    sys.exit(0 if same else 1)


if __name__ == "__main__":
    main(sys.argv[1])
