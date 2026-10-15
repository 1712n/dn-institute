"""Core types: parsed trade events, violation reasons and quarantine entries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

# Times given without a date (HH:MM:SS) are placed on this day so they can be
# compared; a feed that gives times only is taken to cover a single day. The
# day itself never reaches the output.
TIME_ONLY_DATE = date.min

# A CSV row as read by csv.DictReader, before any conversion. Fields missing
# from a short row are None; fields beyond the header are kept as a list under
# the key None, which can't collide with a column name.
RawRow = dict[Optional[str], Union[str, list[str], None]]


class StrEnum(str, Enum):
    """Like enum.StrEnum (Python 3.11+): each member is, and prints as, its value."""

    def __str__(self) -> str:
        return self.value


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class Reason(StrEnum):
    """Why a row was quarantined. Values are stable codes written to the output."""

    # The row can't be parsed into a typed event.
    MALFORMED_ROW = "malformed_row"
    INVALID_TIMESTAMP = "invalid_timestamp"
    INVALID_AMOUNT = "invalid_amount"
    INVALID_SIDE = "invalid_side"

    # Schema: a required value is empty.
    MISSING_REQUIRED_VALUE = "missing_required_value"

    # Identity: the row repeats a trade already seen.
    SUSPECTED_DUPLICATE = "suspected_duplicate"

    # Invariants: the values can't all be true.
    INGESTED_BEFORE_BLOCK = "ingested_before_block"


class Flag(StrEnum):
    """What resolution changed or verified on a loaded event."""

    BLOCK_TIME_BACKFILLED = "block_time_backfilled"
    BLOCK_TIME_CORRECTED = "block_time_corrected"
    INGESTED_AT_UNRELIABLE = "ingested_at_unreliable"
    CONFIRMED_DISTINCT_TRADE = "confirmed_distinct_trade"


class DropReason(StrEnum):
    """Why resolution removed a quarantined row instead of loading it."""

    TX_NOT_FOUND = "tx_not_found"  # not on chain, reverted or reorged out
    DUPLICATE_CONFIRMED = "duplicate_confirmed"


@dataclass(frozen=True)
class Violation:
    reason: Reason
    field: str | None = None
    detail: str = ""


@dataclass(frozen=True)
class TradeEvent:
    """A normalized trade record as delivered by the indexer.

    `block_time` is optional because a missing value is resolvable
    (backfilled from the chain); every other field is required to parse.
    `flags` record what resolution changed or verified before loading.
    """

    event_id: str
    tx_hash: str
    block_time: datetime | None
    wallet: str
    side: Side
    amount: Decimal
    ingested_at: datetime
    flags: frozenset[Flag] = frozenset()


@dataclass(frozen=True)
class QuarantinedRow:
    """A row held back from analytics, with everything needed to trace it.

    `event` is None when the row couldn't be parsed; such rows can't be
    resolved automatically.
    """

    line: int
    raw: RawRow
    violations: tuple[Violation, ...]
    event: TradeEvent | None = None

    @property
    def reasons(self) -> tuple[Reason, ...]:
        return tuple(v.reason for v in self.violations)
