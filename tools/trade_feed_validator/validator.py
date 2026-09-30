"""Validation, de-duplication and conflict detection for raw trade events.

`TradeFeedValidator` is a streaming processor: feed it raw records in arrival
order and it returns exactly one `Outcome` per record. Nothing is dropped
silently: every record is either accepted, recognised as a duplicate of a
named canonical event, or dead-lettered with machine-readable reason codes.

De-duplication state is bounded by a horizon measured in block time, so the
validator can run over an unbounded stream in constant memory per horizon.
"""

from __future__ import annotations

import heapq
import itertools
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import Callable, TypeVar

REQUIRED_FIELDS = ("event_id", "tx_hash", "block_time", "wallet", "side", "amount", "ingested_at")
# Used as the trade identity when present: one on-chain log is one trade.
OPTIONAL_FIELDS = ("log_index",)
MISSING_TOKENS = frozenset({"", "null", "none"})
SIDES = frozenset({"BUY", "SELL"})
# A token amount is at most a uint256 in its smallest unit, so no amount in
# any unit can be larger. Anything above is corrupt, not a trade.
MAX_AMOUNT = Decimal(2**256 - 1)

_TIME_ONLY = re.compile(r"\d{2}:\d{2}:\d{2}(\.\d{1,6})?")
_NUMBER = re.compile(r"\d+(\.\d+)?([eE][+-]?\d+)?")
_HEX_ID = re.compile(r"0x[0-9a-fA-F]+")
_STRICT_IDS = {
    "tx_hash": re.compile(r"0x[0-9a-f]{64}"),
    "wallet": re.compile(r"0x[0-9a-f]{40}"),
}

T = TypeVar("T")


class Status(str, Enum):
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"
    DEAD_LETTER = "dead_letter"


class ConfigError(Exception):
    """The feed cannot be interpreted with the given configuration."""


@dataclass(frozen=True)
class Config:
    # Anchors time-only timestamps (HH:MM:SS, UTC) such as the sample feed's.
    feed_date: date | None = None
    # Tolerated disagreement between the chain clock and the ingestion clock.
    max_clock_skew: timedelta = timedelta(seconds=30)
    # Accepted events that took longer than this to arrive are flagged.
    max_ingestion_lag: timedelta = timedelta(minutes=1)
    # How far behind the newest accepted block time a duplicate is still caught.
    dedup_horizon: timedelta = timedelta(hours=24)
    # Earlier block times are placeholders (e.g. a null parsed as epoch 0).
    # Default: the Bitcoin genesis block (2009-01-03), older than any public chain.
    min_block_time: datetime = datetime(2009, 1, 3, tzinfo=timezone.utc)
    # Upper bound for ingested_at; None disables the check.
    now: datetime | None = None
    # Require full-length EVM identifiers (the sample's shortened ones fail).
    strict_identifiers: bool = False


@dataclass(frozen=True)
class Trade:
    event_id: str
    tx_hash: str
    block_time: datetime
    wallet: str
    side: str
    amount: Decimal
    ingested_at: datetime
    log_index: int | None = None

    @property
    def natural_key(self) -> tuple:
        """Identity of the on-chain trade, independent of the indexer's event_id."""
        if self.log_index is not None:
            return (self.tx_hash, self.log_index)
        return (self.tx_hash, self.wallet, self.side, self.amount)

    @property
    def payload(self) -> tuple:
        """Fields that must agree for two records to describe the same trade."""
        return (self.tx_hash, self.block_time, self.wallet, self.side, self.amount, self.log_index)

    @property
    def ingestion_lag(self) -> timedelta:
        return self.ingested_at - self.block_time


@dataclass(frozen=True)
class Outcome:
    status: Status
    reasons: tuple[str, ...] = ()
    trade: Trade | None = None
    # Canonical event for a duplicate; the conflicting event for a conflict.
    related_event: str | None = None
    # Non-blocking observations about an accepted trade.
    flags: tuple[str, ...] = ()


def parse_timestamp(value: str, feed_date: date | None) -> datetime:
    """Parse an ISO-8601 timestamp with offset, or HH:MM:SS anchored to feed_date (UTC)."""
    if _TIME_ONLY.fullmatch(value):
        if feed_date is None:
            raise ConfigError(f"time-only timestamp {value!r} needs a feed date")
        return datetime.combine(feed_date, time.fromisoformat(value), timezone.utc)
    # fromisoformat() accepts a "Z" suffix only from Python 3.11.
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value)
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp {value!r} has no UTC offset")
    return parsed.astimezone(timezone.utc)


def parse_amount(value: str) -> Decimal:
    """Parse a positive decimal amount; rejects signs, NaN, infinity and separators."""
    if not _NUMBER.fullmatch(value):
        raise ValueError(f"amount {value!r} is not a plain decimal number")
    amount = Decimal(value)
    if not 0 < amount <= MAX_AMOUNT:
        raise ValueError(f"amount {value!r} is out of range")
    return amount


def parse_side(value: str) -> str:
    side = value.upper()
    if side not in SIDES:
        raise ValueError(f"side {value!r} is not BUY or SELL")
    return side


def parse_log_index(value: str) -> int:
    if not value.isdigit():
        raise ValueError(f"log_index {value!r} is not a non-negative integer")
    return int(value)


def parse_record(record: Mapping[str, str | None], config: Config) -> tuple[Trade | None, list[str]]:
    """Turn a raw record into a Trade, or return every reason it cannot be one."""
    values = {name: _clean(record.get(name)) for name in REQUIRED_FIELDS + OPTIONAL_FIELDS}
    errors = [f"missing_{name}" for name in REQUIRED_FIELDS if values[name] is None]

    tx_hash = _normalize_id(values["tx_hash"])
    wallet = _normalize_id(values["wallet"])
    if config.strict_identifiers:
        for name, value in (("tx_hash", tx_hash), ("wallet", wallet)):
            if value is not None and not _STRICT_IDS[name].fullmatch(value):
                errors.append(f"invalid_{name}")

    def timestamp(value: str) -> datetime:
        return parse_timestamp(value, config.feed_date)

    block_time = _parse(values, "block_time", timestamp, errors)
    ingested_at = _parse(values, "ingested_at", timestamp, errors)
    side = _parse(values, "side", parse_side, errors)
    amount = _parse(values, "amount", parse_amount, errors)
    log_index = _parse(values, "log_index", parse_log_index, errors)
    if errors:
        return None, errors
    trade = Trade(values["event_id"], tx_hash, block_time, wallet, side, amount, ingested_at, log_index)
    return trade, []


class TradeFeedValidator:
    """Stateful validator; one instance per feed (or per partition of a feed)."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        # Each index maps a key to (block_time, value) so it can expire.
        self._events: dict[str, tuple[datetime, tuple]] = {}  # event_id -> payload
        self._trades: dict[tuple, tuple[datetime, tuple[str, tuple]]] = {}  # natural key -> (event_id, payload)
        self._tx_blocks: dict[str, tuple[datetime, str]] = {}  # tx_hash -> event_id
        self._expiry: list[tuple[datetime, int, dict, object]] = []
        self._seq = itertools.count()
        # Newest block time accepted so far.
        self.watermark: datetime | None = None

    @property
    def state_size(self) -> int:
        return len(self._events) + len(self._trades) + len(self._tx_blocks)

    def process(self, record: Mapping[str, str | None]) -> Outcome:
        trade, errors = parse_record(record, self.config)
        if trade is None:
            return Outcome(Status.DEAD_LETTER, tuple(errors))
        errors = self._check_times(trade)
        if errors:
            return Outcome(Status.DEAD_LETTER, tuple(errors), trade)
        return self._deduplicate(trade)

    def _check_times(self, trade: Trade) -> list[str]:
        cfg = self.config
        errors = []
        if trade.block_time < cfg.min_block_time:
            errors.append("block_time_before_min")
        # A trade cannot be ingested before the block that contains it exists.
        if trade.block_time - trade.ingested_at > cfg.max_clock_skew:
            errors.append("block_time_after_ingestion")
        if cfg.now is not None and trade.ingested_at - cfg.now > cfg.max_clock_skew:
            errors.append("ingested_at_in_future")
        # Older events may duplicate something already evicted from state, so
        # accepting them would silently break the uniqueness guarantee.
        if self.watermark is not None and self.watermark - trade.block_time > cfg.dedup_horizon:
            errors.append("beyond_dedup_horizon")
        return errors

    def _deduplicate(self, trade: Trade) -> Outcome:
        seen = self._events.get(trade.event_id)
        if seen is not None:
            if seen[1] == trade.payload:
                return Outcome(Status.DUPLICATE, ("duplicate_event_id",), trade, trade.event_id)
            return Outcome(Status.DEAD_LETTER, ("conflicting_event_id",), trade, trade.event_id)

        # A transaction is mined in exactly one block. Checked before the
        # natural key so a disagreeing copy is surfaced, not dropped as a duplicate.
        tx = self._tx_blocks.get(trade.tx_hash)
        if tx is not None and tx[0] != trade.block_time:
            return Outcome(Status.DEAD_LETTER, ("conflicting_block_time",), trade, tx[1])

        canonical = self._trades.get(trade.natural_key)
        if canonical is not None:
            event_id, payload = canonical[1]
            if payload != trade.payload:
                return Outcome(Status.DEAD_LETTER, ("conflicting_payload",), trade, event_id)
            # Reserve the redelivered event_id so it cannot be reused for another trade.
            self._remember(self._events, trade.event_id, trade.block_time, trade.payload)
            return Outcome(Status.DUPLICATE, ("duplicate_trade",), trade, event_id)

        return self._accept(trade)

    def _accept(self, trade: Trade) -> Outcome:
        flags = []
        if trade.ingestion_lag > self.config.max_ingestion_lag:
            flags.append("high_ingestion_lag")
        if self.watermark is not None and trade.block_time < self.watermark:
            flags.append("late_arrival")

        self._remember(self._events, trade.event_id, trade.block_time, trade.payload)
        self._remember(self._trades, trade.natural_key, trade.block_time, (trade.event_id, trade.payload))
        if trade.tx_hash not in self._tx_blocks:
            self._remember(self._tx_blocks, trade.tx_hash, trade.block_time, trade.event_id)

        if self.watermark is None or trade.block_time > self.watermark:
            self.watermark = trade.block_time
            self._evict()
        return Outcome(Status.ACCEPTED, (), trade, flags=tuple(flags))

    def _remember(self, index: dict, key: object, block_time: datetime, value: object) -> None:
        index[key] = (block_time, value)
        heapq.heappush(self._expiry, (block_time, next(self._seq), index, key))

    def _evict(self) -> None:
        horizon = self.config.dedup_horizon
        while self._expiry and self.watermark - self._expiry[0][0] > horizon:
            block_time, _, index, key = heapq.heappop(self._expiry)
            if key in index and index[key][0] == block_time:
                del index[key]


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return None if value.lower() in MISSING_TOKENS else value


def _normalize_id(value: str | None) -> str | None:
    # EVM hex identifiers are case-insensitive; mixed case is only an EIP-55
    # checksum, so 0xAB.. and 0xab.. must deduplicate to the same key.
    if value is not None and _HEX_ID.fullmatch(value):
        return value.lower()
    return value


def _parse(values: Mapping[str, str | None], name: str, parser: Callable[[str], T], errors: list[str]) -> T | None:
    value = values[name]
    if value is None:
        return None
    try:
        return parser(value)
    except (ValueError, OverflowError):
        errors.append(f"invalid_{name}")
        return None
