"""Streaming validator for trade events coming from a blockchain indexer.

It replaces the naive ``parse -> insert`` loop with ``parse -> validate ->
route``. Every event gets exactly one decision:

* ``ACCEPTED``    - safe to insert into the analytics table (may carry warnings);
* ``DUPLICATE``   - the same trade was already accepted, drop it;
* ``DEAD_LETTER`` - the event is broken and must not reach analytics, park it
                    with the reasons so it can be fixed and replayed.

Library usage::

    validator = TradeFeedValidator()
    for raw in feed_stream:
        decision = validator.process(raw)
        if decision.status is Status.ACCEPTED:
            insert_into(analytics_table, decision.event)
        elif decision.status is Status.DEAD_LETTER:
            send_to_dead_letter_queue(raw, decision.issues)

Only the Python standard library is used.
"""

from __future__ import annotations

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable, Mapping, Optional

REQUIRED_FIELDS = (
    "event_id",
    "tx_hash",
    "block_time",
    "wallet",
    "side",
    "amount",
    "ingested_at",
)
NULL_TOKENS = {"", "null", "none", "nil", "nan", "n/a"}
VALID_SIDES = {"BUY", "SELL"}

# Time-only values ("09:14:02") carry no date. The sample feed is documented as
# "all events on the same day", so any fixed date preserves ordering.
DEFAULT_FEED_DATE = date(1970, 1, 1)


class Status(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    DEAD_LETTER = "DEAD_LETTER"


class Severity(str, enum.Enum):
    ERROR = "ERROR"  # event is routed to the dead-letter queue
    DUPLICATE = "DUPLICATE"  # event is dropped
    WARNING = "WARNING"  # event is accepted but flagged


class Issue(str, enum.Enum):
    # errors -> dead-letter queue
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_SIDE = "INVALID_SIDE"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    INGESTED_BEFORE_BLOCK_TIME = "INGESTED_BEFORE_BLOCK_TIME"
    TX_BLOCK_TIME_CONFLICT = "TX_BLOCK_TIME_CONFLICT"
    EVENT_ID_CONFLICT = "EVENT_ID_CONFLICT"
    # duplicates -> dropped
    DUPLICATE_EVENT_ID = "DUPLICATE_EVENT_ID"
    DUPLICATE_TRADE = "DUPLICATE_TRADE"
    # warnings -> accepted, flagged for analysts
    INGEST_CLOCK_WENT_BACKWARDS = "INGEST_CLOCK_WENT_BACKWARDS"
    LATE_ARRIVAL = "LATE_ARRIVAL"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    ROUND_TRIP = "ROUND_TRIP"


SEVERITY = {
    Issue.MISSING_FIELD: Severity.ERROR,
    Issue.INVALID_SIDE: Severity.ERROR,
    Issue.INVALID_AMOUNT: Severity.ERROR,
    Issue.INVALID_TIMESTAMP: Severity.ERROR,
    Issue.INGESTED_BEFORE_BLOCK_TIME: Severity.ERROR,
    Issue.TX_BLOCK_TIME_CONFLICT: Severity.ERROR,
    Issue.EVENT_ID_CONFLICT: Severity.ERROR,
    Issue.DUPLICATE_EVENT_ID: Severity.DUPLICATE,
    Issue.DUPLICATE_TRADE: Severity.DUPLICATE,
    Issue.INGEST_CLOCK_WENT_BACKWARDS: Severity.WARNING,
    Issue.LATE_ARRIVAL: Severity.WARNING,
    Issue.OUT_OF_ORDER: Severity.WARNING,
    Issue.ROUND_TRIP: Severity.WARNING,
}


@dataclass(frozen=True)
class Finding:
    issue: Issue
    message: str

    @property
    def severity(self) -> Severity:
        return SEVERITY[self.issue]

    def __str__(self) -> str:
        return f"{self.issue.value}: {self.message}"


@dataclass(frozen=True)
class TradeEvent:
    """A parsed, normalised trade event."""

    event_id: str
    tx_hash: str
    block_time: datetime
    wallet: str
    side: str
    amount: Decimal
    ingested_at: datetime

    @property
    def trade_key(self) -> tuple:
        """Identity of the on-chain trade, independent of how it was delivered.

        ``event_id`` and ``ingested_at`` describe the delivery, not the trade,
        so they are excluded. ``tx_hash`` alone is not enough: one transaction
        can legitimately contain several trades (multi-hop swaps, batch fills).
        """
        return (self.tx_hash, self.wallet, self.side, self.amount, self.block_time)


@dataclass
class Decision:
    status: Status
    raw: Mapping[str, Optional[str]]
    event: Optional[TradeEvent] = None
    issues: list[Finding] = field(default_factory=list)
    duplicate_of: Optional[str] = None

    @property
    def event_id(self) -> str:
        return (self.raw.get("event_id") or "").strip()

    def has(self, issue: Issue) -> bool:
        return any(f.issue is issue for f in self.issues)


def is_null(value: Optional[str]) -> bool:
    return value is None or value.strip().lower() in NULL_TOKENS


def normalize_id(value: str) -> str:
    """Strip whitespace; lowercase EVM hex identifiers.

    EVM addresses and hashes are case-insensitive (mixed case is only an
    EIP-55 checksum), so ``0xAbC`` and ``0xabc`` are the same wallet. Other
    chains (e.g. Solana base58) are case-sensitive and are left untouched.
    """
    value = value.strip()
    if value[:2].lower() == "0x":
        return value.lower()
    return value


def parse_timestamp(value: str, feed_date: date = DEFAULT_FEED_DATE) -> datetime:
    """Parse a timestamp into an aware UTC datetime.

    Accepts ``HH:MM:SS`` (combined with ``feed_date``), ISO 8601 (naive values
    are treated as UTC) and Unix epoch seconds or milliseconds.
    """
    value = value.strip()
    if value.isdigit():
        epoch = int(value)
        if epoch > 10**11:  # milliseconds
            epoch_seconds = epoch / 1000
        else:
            epoch_seconds = epoch
        return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
    try:
        parsed_time = time.fromisoformat(value)
    except ValueError:
        pass
    else:
        if parsed_time.tzinfo is None:
            parsed_time = parsed_time.replace(tzinfo=timezone.utc)
        return datetime.combine(feed_date, parsed_time).astimezone(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_event(
    raw: Mapping[str, Optional[str]], feed_date: date = DEFAULT_FEED_DATE
) -> tuple[Optional[TradeEvent], list[Finding]]:
    """Schema and value checks for a single event, no cross-event state."""
    findings: list[Finding] = []

    missing = [name for name in REQUIRED_FIELDS if is_null(raw.get(name))]
    for name in missing:
        findings.append(Finding(Issue.MISSING_FIELD, f"'{name}' is missing"))

    side = None
    if "side" not in missing:
        side = raw["side"].strip().upper()
        if side not in VALID_SIDES:
            findings.append(
                Finding(Issue.INVALID_SIDE, f"side {raw['side']!r} is not BUY/SELL")
            )

    amount = None
    if "amount" not in missing:
        try:
            amount = Decimal(raw["amount"].strip())
        except InvalidOperation:
            amount = None
        if amount is None or not amount.is_finite() or amount <= 0:
            findings.append(
                Finding(
                    Issue.INVALID_AMOUNT,
                    f"amount {raw['amount']!r} is not a positive number",
                )
            )

    timestamps: dict[str, datetime] = {}
    for name in ("block_time", "ingested_at"):
        if name in missing:
            continue
        try:
            timestamps[name] = parse_timestamp(raw[name], feed_date)
        except ValueError:
            findings.append(
                Finding(
                    Issue.INVALID_TIMESTAMP, f"{name} {raw[name]!r} is not a timestamp"
                )
            )

    if findings:
        return None, findings
    return (
        TradeEvent(
            event_id=raw["event_id"].strip(),
            tx_hash=normalize_id(raw["tx_hash"]),
            block_time=timestamps["block_time"],
            wallet=normalize_id(raw["wallet"]),
            side=side,
            amount=amount,
            ingested_at=timestamps["ingested_at"],
        ),
        [],
    )


def _fmt(seconds: float) -> str:
    return f"{seconds:g}s"


class TradeFeedValidator:
    """Stateful validator: call :meth:`process` once per event, in arrival order.

    Only accepted events are remembered. A dead-lettered event can therefore be
    fixed and replayed with the same ``event_id`` and still be accepted.

    State grows with the number of accepted events. For an unbounded stream it
    should be kept in a keyed store with a TTL longer than the indexer's
    maximum redelivery delay.
    """

    def __init__(
        self,
        *,
        feed_date: date = DEFAULT_FEED_DATE,
        clock_skew_tolerance: timedelta = timedelta(seconds=5),
        ingest_clock_tolerance: timedelta = timedelta(seconds=60),
        max_ingest_lag: timedelta = timedelta(minutes=5),
        allowed_lateness: timedelta = timedelta(0),
        round_trip_window: timedelta = timedelta(hours=1),
    ) -> None:
        self.feed_date = feed_date
        self.clock_skew_tolerance = clock_skew_tolerance
        self.ingest_clock_tolerance = ingest_clock_tolerance
        self.max_ingest_lag = max_ingest_lag
        self.allowed_lateness = allowed_lateness
        self.round_trip_window = round_trip_window

        self._by_event_id: dict[str, TradeEvent] = {}
        self._by_trade_key: dict[tuple, str] = {}
        self._block_time_by_tx: dict[str, tuple[datetime, str]] = {}
        self._accepted_by_wallet: dict[str, list[TradeEvent]] = defaultdict(list)
        self._max_ingested_at: Optional[datetime] = None
        self._max_block_time: Optional[datetime] = None

    def process(self, raw: Mapping[str, Optional[str]]) -> Decision:
        event, issues = parse_event(raw, self.feed_date)
        issues = self._check_ingest_clock(raw) + issues
        if event is None:
            return Decision(Status.DEAD_LETTER, raw, issues=issues)

        # 1. Same event_id delivered again.
        previous = self._by_event_id.get(event.event_id)
        if previous is not None:
            if previous.trade_key == event.trade_key:
                issues.append(
                    Finding(Issue.DUPLICATE_EVENT_ID, "event_id already processed")
                )
                return Decision(
                    Status.DUPLICATE,
                    raw,
                    event,
                    issues,
                    duplicate_of=previous.event_id,
                )
            issues.append(
                Finding(
                    Issue.EVENT_ID_CONFLICT,
                    "event_id reused with a different payload",
                )
            )
            return Decision(Status.DEAD_LETTER, raw, event, issues)

        # 2. Impossible timeline: recorded before it happened.
        lead = (event.block_time - event.ingested_at).total_seconds()
        if lead > self.clock_skew_tolerance.total_seconds():
            issues.append(
                Finding(
                    Issue.INGESTED_BEFORE_BLOCK_TIME,
                    f"ingested_at is {_fmt(lead)} before block_time "
                    f"(tolerance {_fmt(self.clock_skew_tolerance.total_seconds())})",
                )
            )
            return Decision(Status.DEAD_LETTER, raw, event, issues)

        # 3. Same trade delivered under a new event_id.
        original_id = self._by_trade_key.get(event.trade_key)
        if original_id is not None:
            issues.append(
                Finding(
                    Issue.DUPLICATE_TRADE,
                    f"same trade already accepted as {original_id}",
                )
            )
            return Decision(
                Status.DUPLICATE, raw, event, issues, duplicate_of=original_id
            )

        # 4. A transaction is mined in exactly one block.
        known = self._block_time_by_tx.get(event.tx_hash)
        if known is not None and known[0] != event.block_time:
            issues.append(
                Finding(
                    Issue.TX_BLOCK_TIME_CONFLICT,
                    f"tx already seen with a different block_time in {known[1]}",
                )
            )
            return Decision(Status.DEAD_LETTER, raw, event, issues)

        issues.extend(self._warnings(event))
        self._accept(event)
        return Decision(Status.ACCEPTED, raw, event, issues)

    def process_all(self, raws: Iterable[Mapping[str, Optional[str]]]) -> list[Decision]:
        return [self.process(raw) for raw in raws]

    def _check_ingest_clock(self, raw: Mapping[str, Optional[str]]) -> list[Finding]:
        """Arrival order must match ingestion time, otherwise a clock is off."""
        if is_null(raw.get("ingested_at")):
            return []
        try:
            ingested_at = parse_timestamp(raw["ingested_at"], self.feed_date)
        except ValueError:
            return []
        findings = []
        if self._max_ingested_at is not None:
            drop = (self._max_ingested_at - ingested_at).total_seconds()
            if drop > self.ingest_clock_tolerance.total_seconds():
                findings.append(
                    Finding(
                        Issue.INGEST_CLOCK_WENT_BACKWARDS,
                        f"ingested_at is {_fmt(drop)} earlier than an event "
                        f"that arrived before it",
                    )
                )
        if self._max_ingested_at is None or ingested_at > self._max_ingested_at:
            self._max_ingested_at = ingested_at
        return findings

    def _warnings(self, event: TradeEvent) -> list[Finding]:
        findings = []

        lag = (event.ingested_at - event.block_time).total_seconds()
        if lag > self.max_ingest_lag.total_seconds():
            findings.append(
                Finding(
                    Issue.LATE_ARRIVAL,
                    f"ingested {_fmt(lag)} after block_time "
                    f"(max {_fmt(self.max_ingest_lag.total_seconds())})",
                )
            )

        if self._max_block_time is not None:
            behind = (self._max_block_time - event.block_time).total_seconds()
            if behind > self.allowed_lateness.total_seconds():
                findings.append(
                    Finding(
                        Issue.OUT_OF_ORDER,
                        f"block_time is {_fmt(behind)} older than an already "
                        f"accepted event; time windows that include it must be "
                        f"recomputed",
                    )
                )

        opposite = "SELL" if event.side == "BUY" else "BUY"
        for other in self._accepted_by_wallet[event.wallet]:
            gap = abs(event.block_time - other.block_time)
            if (
                other.side == opposite
                and other.amount == event.amount
                and gap <= self.round_trip_window
            ):
                findings.append(
                    Finding(
                        Issue.ROUND_TRIP,
                        f"same wallet {other.side} of the same amount in "
                        f"{other.event_id}, {_fmt(gap.total_seconds())} apart",
                    )
                )
                break

        return findings

    def _accept(self, event: TradeEvent) -> None:
        self._by_event_id[event.event_id] = event
        self._by_trade_key[event.trade_key] = event.event_id
        self._block_time_by_tx.setdefault(
            event.tx_hash, (event.block_time, event.event_id)
        )
        self._accepted_by_wallet[event.wallet].append(event)
        if self._max_block_time is None or event.block_time > self._max_block_time:
            self._max_block_time = event.block_time
