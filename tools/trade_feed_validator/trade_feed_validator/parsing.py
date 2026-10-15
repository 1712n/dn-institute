"""Read a CSV feed and turn its rows into typed events.

Parsing never raises on a bad row: every problem becomes a Violation, so one
corrupt record can't stop the run. Only a header without the required columns
is fatal, because then no row can be interpreted.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, time
from decimal import Decimal
from pathlib import Path

from .models import TIME_ONLY_DATE, RawRow, Reason, Side, TradeEvent, Violation

COLUMNS = (
    "event_id",
    "tx_hash",
    "block_time",
    "wallet",
    "side",
    "amount",
    "ingested_at",
)

# Values treated as missing, compared case-insensitively after stripping.
NULL_TOKENS = frozenset({"", "null"})

# Plain decimal notation only: exponents like 1e999999999 are valid Decimals
# but can't be written back out in reasonable time or space.
AMOUNT_PATTERN = re.compile(r"\d+(\.\d+)?")

# A time of day without a date, taken as UTC.
TIME_PATTERN = re.compile(r"(\d{2}):(\d{2}):(\d{2})")


class FeedSchemaError(ValueError):
    """The feed's header lacks required columns or repeats a column name."""


@dataclass(frozen=True)
class ParsedRow:
    line: int
    raw: RawRow
    event: TradeEvent | None
    violations: tuple[Violation, ...]


def read_rows(path: str | Path) -> Iterator[tuple[int, RawRow]]:
    """Yield (line number, raw row) for each data row of a CSV feed.

    The line number is where the record ends, which differs from where it
    starts only if a quoted field spans several lines.
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        missing = [c for c in COLUMNS if c not in header]
        if missing:
            raise FeedSchemaError(f"missing columns: {', '.join(missing)}")
        repeated = sorted({c for c in header if header.count(c) > 1})
        if repeated:
            # DictReader would keep only the last value of a repeated column.
            raise FeedSchemaError(f"repeated columns: {', '.join(repeated)}")
        for raw in reader:
            yield reader.line_num, raw


def parse_row(line: int, raw: RawRow) -> ParsedRow:
    """Convert a raw row into a TradeEvent, collecting every violation found.

    The event is built only when all values parse. The one exception is a
    missing block_time: the row stays a typed event (with block_time None) so
    it can be backfilled from the chain later.
    """
    if None in raw or any(raw.get(c) is None for c in COLUMNS):
        detail = f"expected {len(COLUMNS)} fields"
        return ParsedRow(line, raw, None, (Violation(Reason.MALFORMED_ROW, None, detail),))

    violations: list[Violation] = []
    values: dict[str, object] = {}
    for column in COLUMNS:
        text = raw[column].strip()
        if text.lower() in NULL_TOKENS:
            violations.append(Violation(Reason.MISSING_REQUIRED_VALUE, column))
            values[column] = None
            continue
        parser, reason = _PARSERS.get(column, (str, None))
        try:
            values[column] = parser(text)
        except ValueError as e:
            violations.append(Violation(reason, column, str(e)))

    resolvable = all(
        v.reason is Reason.MISSING_REQUIRED_VALUE and v.field == "block_time"
        for v in violations
    )
    event = TradeEvent(**values) if resolvable else None
    return ParsedRow(line, raw, event, tuple(violations))


def _parse_side(text: str) -> Side:
    try:
        return Side(text)
    except ValueError:
        raise ValueError(f"expected BUY or SELL, got {text!r}") from None


def _parse_amount(text: str) -> Decimal:
    if not AMOUNT_PATTERN.fullmatch(text):
        raise ValueError(f"not a plain decimal number: {text!r}")
    amount = Decimal(text)
    if amount <= 0:
        raise ValueError(f"must be positive, got {text!r}")
    return amount


def _parse_timestamp(text: str) -> datetime:
    if match := TIME_PATTERN.fullmatch(text):
        # Built from the fields, not time.fromisoformat, which reads 24:00:00
        # as midnight on some Python versions and rejects it on others.
        try:
            return datetime.combine(TIME_ONLY_DATE, time(*map(int, match.groups())), tzinfo=UTC)
        except ValueError:
            raise ValueError(f"not a valid time: {text!r}") from None
    try:
        ts = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError(f"not an ISO 8601 timestamp or HH:MM:SS time: {text!r}") from None
    if ts.tzinfo is None:
        raise ValueError(f"timestamp has no timezone: {text!r}")
    try:
        return ts.astimezone(UTC)
    except OverflowError:
        raise ValueError(f"timestamp out of range in UTC: {text!r}") from None


_PARSERS: dict[str, tuple[Callable[[str], object], Reason]] = {
    "side": (_parse_side, Reason.INVALID_SIDE),
    "amount": (_parse_amount, Reason.INVALID_AMOUNT),
    "block_time": (_parse_timestamp, Reason.INVALID_TIMESTAMP),
    "ingested_at": (_parse_timestamp, Reason.INVALID_TIMESTAMP),
}
