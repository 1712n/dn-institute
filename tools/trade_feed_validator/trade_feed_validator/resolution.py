"""Resolve quarantined rows against authoritative sources.

The chain answers transaction facts: whether a transaction exists and is
final, and its block time. It knows nothing about trades, which are the
indexer's reading of a transaction's logs, so trade counts come from decoding
the transaction afresh, independent of the feed that delivered the row. Trade
content (wallet, side, amount) is the indexer's responsibility and is trusted,
as it is for clean rows.

Both sources are behind the ChainResolver interface. The run uses
DummyChainResolver (dummy_resolver.py), whose answers are synthetic.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from decimal import Decimal
from typing import Protocol

from .checks import TradeKey, check_invariants, trade_key
from .models import DropReason, Flag, QuarantinedRow, Reason, Side, TradeEvent
from .pipeline import Validator


@dataclass(frozen=True)
class TxLookup:
    """The chain's answer about a transaction.

    `block_time` is the time of the block holding the confirmed, final
    transaction, or None if it isn't on chain (never mined, reverted or
    reorged out). It must be timezone-aware and is converted to UTC, like
    timestamps parsed from the feed.
    """

    block_time: datetime | None

    def __post_init__(self) -> None:
        if self.block_time is None:
            return
        if self.block_time.tzinfo is None:
            raise ValueError(f"block_time must be timezone-aware, got {self.block_time.isoformat()}")
        object.__setattr__(self, "block_time", self.block_time.astimezone(timezone.utc))


class ChainResolver(Protocol):
    def lookup_tx(self, tx_hash: str) -> TxLookup | None:
        """TxLookup(None) if the transaction isn't on chain; None if it can't be resolved."""

    def count_matching_trades(self, tx_hash: str, wallet: str, side: Side, amount: Decimal) -> int | None:
        """How many matching trades a fresh decode of the transaction finds; None if it can't be resolved."""


@dataclass(frozen=True)
class DroppedRow:
    row: QuarantinedRow
    reason: DropReason


@dataclass
class ResolutionResult:
    loaded: list[TradeEvent] = field(default_factory=list)
    dropped: list[DroppedRow] = field(default_factory=list)
    quarantined: list[QuarantinedRow] = field(default_factory=list)


def resolve(
    rows: Iterable[QuarantinedRow], resolver: ChainResolver, validator: Validator
) -> ResolutionResult:
    """Resolve quarantined rows in one pass, in arrival order.

    `validator` must be the one that produced the rows: once a row's
    block_time is resolved, it is matched for duplicates against the trades
    the validator has already seen.
    """
    result = ResolutionResult()
    occurrences: dict[TradeKey, int] = {}
    for row in rows:
        outcome = _resolve_row(row, resolver, validator, occurrences)
        if isinstance(outcome, TradeEvent):
            result.loaded.append(outcome)
        elif isinstance(outcome, DroppedRow):
            result.dropped.append(outcome)
        else:
            result.quarantined.append(outcome)
    return result


def _resolve_row(
    row: QuarantinedRow,
    resolver: ChainResolver,
    validator: Validator,
    occurrences: dict[TradeKey, int],
) -> TradeEvent | DroppedRow | QuarantinedRow:
    event = row.event
    if event is None:
        return row  # unparseable: needs a person, not the chain

    flags = set(event.flags)
    duplicates = [v for v in row.violations if v.reason is Reason.SUSPECTED_DUPLICATE]

    # Missing or impossible block_time: take the time from the chain, then
    # match duplicates on it (the row wasn't matched while its time was untrusted).
    if {Reason.MISSING_REQUIRED_VALUE, Reason.INGESTED_BEFORE_BLOCK} & set(row.reasons):
        lookup = resolver.lookup_tx(event.tx_hash)
        if lookup is None:
            return row
        if lookup.block_time is None:
            return DroppedRow(row, DropReason.TX_NOT_FOUND)
        if lookup.block_time != event.block_time:
            flags.add(Flag.BLOCK_TIME_BACKFILLED if event.block_time is None else Flag.BLOCK_TIME_CORRECTED)
            event = replace(event, block_time=lookup.block_time)
        if check_invariants(event):
            # block_time is now verified, so the ingest clock is what's wrong.
            flags.add(Flag.INGESTED_AT_UNRELIABLE)
        duplicates = validator.duplicates.check(event)

    # Suspected duplicate: a fresh decode says how many such trades really exist,
    # and records beyond that count are duplicates.
    if duplicates:
        key = trade_key(event)
        occurrence = occurrences[key] = occurrences.get(key, 1) + 1  # the first record is 1
        count = resolver.count_matching_trades(event.tx_hash, event.wallet, event.side, event.amount)
        if count is None:
            return replace(row, event=replace(event, flags=frozenset(flags)), violations=tuple(duplicates))
        if occurrence > count:
            return DroppedRow(row, DropReason.DUPLICATE_CONFIRMED)
        flags.add(Flag.CONFIRMED_DISTINCT_TRADE)

    return replace(event, flags=frozenset(flags))
