"""Test doubles shared across test modules."""

from datetime import UTC, datetime, time
from decimal import Decimal

from trade_feed_validator.models import TIME_ONLY_DATE, Side
from trade_feed_validator.resolution import TxLookup


def utc(hh, mm, ss):
    """A UTC time of day, as parsed from an HH:MM:SS value."""
    return datetime.combine(TIME_ONLY_DATE, time(hh, mm, ss), tzinfo=UTC)


def trade(tx_hash, wallet, side, amount):
    """A trade as the resolver is asked about it, used as a key for trade counts."""
    return (tx_hash, wallet, Side(side), Decimal(amount))


# The trades behind the sample's suspected duplicates.
EVT_003_TRADE = trade("0xaa2", "0xD4…", "BUY", "120000")
EVT_007_TRADE = trade("0xaa5", "0xF6…", "BUY", "90000")


class MockChainResolver:
    """A ChainResolver with known answers. Anything not listed can't be resolved (None).

    `txs` maps tx_hash to its block time, or to None if it isn't on chain;
    `trades` maps a trade (see `trade`) to the number of matching trades a
    fresh decode finds; only the exact trade asked about gets an answer.
    """

    def __init__(self, txs=None, trades=None):
        self.txs = txs or {}
        self.trades = trades or {}

    def lookup_tx(self, tx_hash):
        return TxLookup(self.txs[tx_hash]) if tx_hash in self.txs else None

    def count_matching_trades(self, tx_hash, wallet, side, amount):
        return self.trades.get((tx_hash, wallet, side, amount))
