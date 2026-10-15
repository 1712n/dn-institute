"""A ChainResolver with synthetic answers that fit the sample feed.

The run uses it so that every quarantined row in the sample goes through
resolution. Its answers are made up, not derived from the data.
"""

from __future__ import annotations

from datetime import UTC, datetime, time
from decimal import Decimal

from .models import TIME_ONLY_DATE, Side
from .resolution import TxLookup

BLOCK_TIMES = {
    "0xaa4": datetime.combine(TIME_ONLY_DATE, time(9, 58, 27), tzinfo=UTC),  # evt_005: block_time missing
    "0xaa6": datetime.combine(TIME_ONLY_DATE, time(10, 10, 0), tzinfo=UTC),  # evt_008: the feed's time is right
}

TRADE_COUNTS = {
    ("0xaa2", "0xD4…", Side.BUY, Decimal("120000")): 1,  # evt_003 repeats evt_002
    ("0xaa5", "0xF6…", Side.BUY, Decimal("90000")): 2,  # evt_006 and evt_007 are two trades
}


class DummyChainResolver:
    """Answers questions about the sample's quarantined rows; anything else can't be resolved."""

    def lookup_tx(self, tx_hash: str) -> TxLookup | None:
        if tx_hash not in BLOCK_TIMES:
            return None
        return TxLookup(BLOCK_TIMES[tx_hash])

    def count_matching_trades(self, tx_hash: str, wallet: str, side: Side, amount: Decimal) -> int | None:
        return TRADE_COUNTS.get((tx_hash, wallet, side, amount))
