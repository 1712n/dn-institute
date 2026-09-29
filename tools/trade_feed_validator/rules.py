"""Validation rules.

Record rules look at one event and annotate it with issues. Cross-record checks
keep state across the stream (deduplication, ordering, ingest clock) or look at
the whole batch (round-trip detection). To add a check, write a function with
the ``RecordRule`` signature and append it to ``RECORD_RULES``.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Hashable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from records import DROP, FLAG, REJECT, TradeEvent


@dataclass(frozen=True)
class Config:
    # Tolerated disagreement between the chain clock and our ingest clock.
    clock_skew: timedelta = timedelta(seconds=5)
    # Ingest lag above this is flagged: it usually means an indexer retry or backlog.
    max_ingest_lag: timedelta = timedelta(minutes=2)
    # Same wallet buying and selling the same amount within this window is flagged.
    round_trip_window: timedelta = timedelta(minutes=30)
    # Require full EVM identifiers (20-byte address, 32-byte tx hash). Off by default
    # because the challenge sample uses shortened ids.
    strict_identifiers: bool = False


RecordRule = Callable[[TradeEvent, Config], None]


def ingested_before_block_time(ev: TradeEvent, cfg: Config) -> None:
    """An event cannot be ingested before the block that contains it was produced."""
    if ev.block_time and ev.ingested_at and ev.ingested_at < ev.block_time - cfg.clock_skew:
        gap = ev.block_time - ev.ingested_at
        ev.add(
            "ingested_before_block_time",
            REJECT,
            f"ingested_at is {_fmt(gap)} before block_time; one of the two clocks is wrong",
        )


def high_ingest_lag(ev: TradeEvent, cfg: Config) -> None:
    if ev.block_time and ev.ingested_at and ev.ingested_at - ev.block_time > cfg.max_ingest_lag:
        ev.add(
            "high_ingest_lag",
            FLAG,
            f"ingested {_fmt(ev.ingested_at - ev.block_time)} after block_time "
            f"(limit {_fmt(cfg.max_ingest_lag)}); typical of an indexer retry",
        )


_EVM_ADDRESS = re.compile(r"^0x[0-9a-f]{40}$")
_EVM_TX_HASH = re.compile(r"^0x[0-9a-f]{64}$")


def identifier_format(ev: TradeEvent, cfg: Config) -> None:
    if not cfg.strict_identifiers:
        return
    if ev.wallet and not _EVM_ADDRESS.match(ev.wallet):
        ev.add("invalid_identifier", REJECT, f"wallet is not a 20-byte hex address: {ev.wallet!r}")
    if ev.tx_hash and not _EVM_TX_HASH.match(ev.tx_hash):
        ev.add("invalid_identifier", REJECT, f"tx_hash is not a 32-byte hex hash: {ev.tx_hash!r}")


RECORD_RULES: list[RecordRule] = [ingested_before_block_time, high_ingest_lag, identifier_format]


def trade_key(ev: TradeEvent) -> tuple[Hashable, ...]:
    """Identity of the on-chain trade, independent of the indexer's event_id.

    With ``log_index`` the key is exact: one log in one transaction. Without it
    the best available key is (tx_hash, wallet, side, amount); two genuinely
    identical fills inside one transaction would collapse into one. The README
    explains why that is the safer failure for this feed.
    """
    if ev.log_index is not None:
        return (ev.tx_hash, ev.log_index)
    return (ev.tx_hash, ev.wallet, ev.side, ev.amount)


_COMPARED_FIELDS = ("wallet", "side", "amount", "block_time")


def _payload(ev: TradeEvent) -> tuple[Hashable, ...]:
    return (ev.tx_hash, ev.log_index, *(getattr(ev, f) for f in _COMPARED_FIELDS))


class Deduplicator:
    """Detects redelivered events and conflicting copies of one trade.

    Accepted events are remembered by event_id and by trade_key; dropped
    duplicates reserve their event_id. Rejected events are not remembered, so
    a dead-lettered row never shadows its own corrected redelivery.
    """

    def __init__(self) -> None:
        self._by_event_id: dict[str, TradeEvent] = {}
        self._by_trade: dict[tuple[Hashable, ...], TradeEvent] = {}

    def check(self, ev: TradeEvent) -> str | None:
        """Annotate ``ev`` and return the event_id it duplicates, if any."""
        seen_id = self._by_event_id.get(ev.event_id)
        if seen_id is not None:
            if _payload(seen_id) == _payload(ev):
                ev.add("duplicate_event", DROP, f"event_id redelivered, first seen at row {seen_id.row}")
                return seen_id.event_id
            if trade_key(seen_id) != trade_key(ev):
                ev.add(
                    "event_id_collision",
                    REJECT,
                    f"event_id already used by row {seen_id.row} for a different trade",
                )
                return None
        seen = self._by_trade.get(trade_key(ev)) or seen_id
        if seen is None:
            return None

        differ = [f for f in _COMPARED_FIELDS if getattr(seen, f) != getattr(ev, f)]
        if differ:
            fields = ", ".join(differ)
            seen.add("disputed_trade", FLAG, f"row {ev.row} reports this trade with a different {fields}")
            ev.add(
                "conflicting_duplicate",
                REJECT,
                f"same trade as {seen.event_id} (row {seen.row}) but {fields} differs; "
                "possible chain reorg or bad re-read, needs a decision, not a silent drop",
            )
            return None
        lag = ev.ingested_at - seen.ingested_at if ev.ingested_at and seen.ingested_at else None
        if lag is None:
            how = "redelivered"
        elif lag <= timedelta(seconds=1):
            how = "emitted twice within one second"
        else:
            how = f"redelivered {_fmt(lag)} later"
        ev.add(
            "duplicate_trade",
            DROP,
            f"same on-chain trade as {seen.event_id} (row {seen.row}) under a new event_id; {how}",
        )
        return seen.event_id

    def remember(self, ev: TradeEvent) -> None:
        self._by_event_id.setdefault(ev.event_id, ev)
        self._by_trade.setdefault(trade_key(ev), ev)

    def reserve_event_id(self, ev: TradeEvent) -> None:
        """A dropped duplicate's event_id is taken: reusing it for another trade is a collision."""
        self._by_event_id.setdefault(ev.event_id, ev)


class OrderTracker:
    """Arrival-order checks for a stream.

    * ``ingest_clock_regression``: ingested_at went backwards compared with rows
      that arrived earlier. Arrival order and our own ingest clock must agree;
      when they don't, our timestamp is suspect even if block_time looks fine.
    * ``late_arrival``: an accepted event belongs before the watermark (latest
      accepted block_time), so consumers that assume time order will misplace it.
    """

    def __init__(self) -> None:
        self._max_ingested: TradeEvent | None = None
        self._watermark: TradeEvent | None = None

    def check_ingest_clock(self, ev: TradeEvent, cfg: Config) -> None:
        top = self._max_ingested
        if ev.ingested_at and top is not None and ev.ingested_at < top.ingested_at - cfg.clock_skew:
            ev.add(
                "ingest_clock_regression",
                FLAG,
                f"ingested_at is {_fmt(top.ingested_at - ev.ingested_at)} earlier than "
                f"{top.event_id} (row {top.row}) which arrived before it",
            )

    def advance_ingest_clock(self, ev: TradeEvent) -> None:
        """Called for rows that were not rejected, so a bad row cannot move the clock."""
        if ev.ingested_at and (self._max_ingested is None or ev.ingested_at > self._max_ingested.ingested_at):
            self._max_ingested = ev

    def observe_accepted(self, ev: TradeEvent) -> None:
        mark = self._watermark
        if mark is not None and ev.block_time < mark.block_time:
            ev.add(
                "late_arrival",
                FLAG,
                f"block_time is {_fmt(mark.block_time - ev.block_time)} older than "
                f"{mark.event_id} (row {mark.row}) which arrived earlier",
            )
        if mark is None or ev.block_time > mark.block_time:
            self._watermark = ev


def find_round_trips(events: list[TradeEvent], cfg: Config) -> list[tuple[TradeEvent, TradeEvent]]:
    """Flag a wallet buying and selling the same amount within the window.

    This is a wash-trading signal, not proof: the trades are real on-chain
    activity, so they stay in the output and carry a flag. Input includes
    dead-lettered events that still have a block_time, so a quarantined leg
    does not hide the pattern; every trade is counted once (by trade_key) and
    each leg is paired at most once, in time order.
    """
    unique: dict[tuple[Hashable, ...], TradeEvent] = {}
    for ev in events:
        if ev.tx_hash and ev.wallet and ev.side and ev.amount is not None and ev.block_time is not None:
            unique.setdefault(trade_key(ev), ev)
    groups: dict[tuple[str, object], list[TradeEvent]] = defaultdict(list)
    for ev in unique.values():
        groups[(ev.wallet, ev.amount)].append(ev)

    pairs: list[tuple[TradeEvent, TradeEvent]] = []
    for group in groups.values():
        group.sort(key=lambda e: (e.block_time, e.row))
        paired: set[int] = set()
        for i, first in enumerate(group):
            if first.row in paired:
                continue
            for second in group[i + 1 :]:
                if second.block_time - first.block_time > cfg.round_trip_window:
                    break
                if second.side != first.side and second.row not in paired:
                    pairs.append((first, second))
                    paired.update((first.row, second.row))
                    break
    for first, second in pairs:
        gap = _fmt(second.block_time - first.block_time)
        first.add("round_trip_suspect", FLAG, f"{first.wallet} reversed by {second.event_id} after {gap}")
        second.add("round_trip_suspect", FLAG, f"{second.wallet} reverses {first.event_id} after {gap}")
    return pairs


def _fmt(delta: timedelta | None) -> str:
    if delta is None:
        return "?"
    seconds = int(delta.total_seconds())
    minutes, seconds = divmod(abs(seconds), 60)
    return f"{minutes}m{seconds:02d}s" if minutes else f"{seconds}s"


def utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt.microsecond == 0 else dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
