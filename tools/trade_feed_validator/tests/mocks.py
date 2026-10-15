"""Test doubles shared across test modules."""

from datetime import UTC, datetime

from trade_feed_validator.resolution import TxLookup


def utc(hh, mm, ss):
    return datetime(2026, 1, 1, hh, mm, ss, tzinfo=UTC)


class MockChainResolver:
    """A ChainResolver with known answers. Anything not listed has no answer yet.

    `txs` maps tx_hash to its block time, or to None if it isn't on chain;
    `trades` maps tx_hash to the number of matching trades a fresh decode finds.
    """

    def __init__(self, txs=None, trades=None):
        self.txs = txs or {}
        self.trades = trades or {}

    def lookup_tx(self, tx_hash):
        return TxLookup(self.txs[tx_hash]) if tx_hash in self.txs else None

    def count_matching_trades(self, tx_hash, wallet, side, amount):
        return self.trades.get(tx_hash)
