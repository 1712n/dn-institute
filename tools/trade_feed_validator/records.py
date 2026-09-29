"""Parsing raw feed rows into typed trade events.

Parsing never raises on bad values: every problem becomes an ``Issue`` so the
row can be routed to the dead-letter queue with its raw fields intact.
Only a broken header (the whole feed is unreadable) raises ``FeedSchemaError``.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
from typing import Callable, Optional

REQUIRED_COLUMNS: tuple[str, ...] = (
    "event_id",
    "tx_hash",
    "block_time",
    "wallet",
    "side",
    "amount",
    "ingested_at",
)
# Optional: when present it becomes part of the trade identity, see rules.trade_key.
LOG_INDEX_COLUMN = "log_index"
# Added to the clean output by the validator, so an input column must not use them.
RESERVED_COLUMNS = ("flags", "source_row")

NULL_TOKENS = frozenset({"", "null", "none", "nan", "n/a", "na", "\\n"})
SIDES = frozenset({"BUY", "SELL"})
# Placeholder day for time-only timestamps when no --feed-date is given.
PLACEHOLDER_DATE = date(1970, 1, 1)

# Parsed by hand instead of datetime.fromisoformat, which accepts different
# formats on different Python versions. Fractions beyond microseconds are truncated.
_TIME = r"(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?"
_TIME_ONLY = re.compile(rf"^{_TIME}$", re.ASCII)
_DATETIME = re.compile(
    rf"^(\d{{4}})-(\d{{2}})-(\d{{2}})[T ]{_TIME}(Z|[+-]\d{{2}}:\d{{2}})?$", re.ASCII | re.IGNORECASE
)
_NUMBER = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$", re.ASCII)
_UNSIGNED_INT = re.compile(r"^\d+$", re.ASCII)
_HEX_ID = re.compile(r"^0[xX][0-9a-fA-F]+$")
# Plausible range for a trade timestamp; also keeps datetime arithmetic away from year 1 and 9999.
_MIN_YEAR, _MAX_YEAR = 1970, 2999
# uint256 has 78 decimal digits; ERC-20 tokens use at most 18 decimals, 36 leaves headroom.
_MAX_INTEGER_DIGITS, _MAX_FRACTION_DIGITS = 78, 36
# Enough precision to add up a large feed of maximum-size amounts without rounding.
AMOUNT_PRECISION = 200

REJECT = "reject"  # row goes to the dead-letter queue for repair and replay
DROP = "drop"  # row is a redelivery of a trade already accepted; nothing to repair
FLAG = "flag"  # row is accepted, the flag travels with it to analytics


class FeedSchemaError(ValueError):
    """The feed cannot be processed at all (missing or repeated columns)."""


@dataclass(frozen=True)
class Issue:
    code: str
    severity: str  # REJECT, DROP or FLAG
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


@dataclass
class RawRow:
    row: int  # 1-based position in arrival order, matches "#" in the issue table
    fields: dict[str, str | None]
    overflow: list[str] = field(default_factory=list)  # values beyond the header


@dataclass
class TradeEvent:
    raw: RawRow
    event_id: str | None = None
    tx_hash: str | None = None
    wallet: str | None = None
    side: str | None = None
    amount: Decimal | None = None
    block_time: datetime | None = None
    ingested_at: datetime | None = None
    log_index: int | None = None
    issues: list[Issue] = field(default_factory=list)

    @property
    def row(self) -> int:
        return self.raw.row

    @property
    def rejected(self) -> bool:
        return any(i.severity == REJECT for i in self.issues)

    @property
    def dropped(self) -> bool:
        return any(i.severity == DROP for i in self.issues)

    @property
    def flags(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == FLAG]

    def add(self, code: str, severity: str, detail: str) -> None:
        if not any(i.code == code for i in self.issues):
            self.issues.append(Issue(code, severity, detail))


def _reject_nul(lines: Iterable[str]) -> Iterator[str]:
    # csv treats NUL differently across Python versions; make it one explicit error.
    for number, line in enumerate(lines, 1):
        if "\0" in line:
            raise FeedSchemaError(f"NUL byte on line {number}")
        yield line


def read_feed(lines: Iterable[str]) -> tuple[list[str], list[RawRow]]:
    """Read CSV text into raw rows. Validates the header, not the values.

    ``strict`` makes an unbalanced quote an error instead of letting it swallow
    every following line into one field; ``csv.Error`` reaches the caller.
    """
    reader = csv.reader(_reject_nul(lines), strict=True)
    header: list[str] = []
    for values in reader:
        if any(v.strip() for v in values):
            header = [h.strip().lstrip("\ufeff") for h in values]
            break
    if not header:
        raise FeedSchemaError("feed is empty: no header row")
    repeated = sorted({h for h in header if header.count(h) > 1})
    if repeated:
        raise FeedSchemaError(f"repeated column(s): {', '.join(repeated)}")
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise FeedSchemaError(f"missing required column(s): {', '.join(missing)}")
    reserved = [c for c in RESERVED_COLUMNS if c in header]
    if reserved:
        raise FeedSchemaError(f"column name(s) reserved for validator output: {', '.join(reserved)}")

    rows: list[RawRow] = []
    for values in reader:
        if not values or all(not v.strip() for v in values):
            continue  # blank line, not a record
        padded = values + [None] * (len(header) - len(values))
        rows.append(
            RawRow(
                row=len(rows) + 1,
                fields=dict(zip(header, padded)),
                overflow=values[len(header) :],
            )
        )
    return header, rows


def is_null(value: str | None) -> bool:
    return value is None or value.strip().lower() in NULL_TOKENS


def normalize_id(value: str) -> str:
    """Hex identifiers (EVM addresses, tx hashes) are case-insensitive: 0xAB == 0xab.

    Anything else (base58 Solana addresses, shortened ids like ``0xD4…``) is
    case-sensitive and kept as is.
    """
    value = value.strip()
    return value.lower() if _HEX_ID.match(value) else value


def is_time_only(value: str | None) -> bool:
    return value is not None and bool(_TIME_ONLY.match(value.strip()))


def parse_timestamp(value: str, feed_date: date | None) -> tuple[datetime | None, str | None]:
    """Return (UTC datetime, None) or (None, error).

    Accepts ISO 8601 date-time with optional offset, or time-only HH:MM:SS on
    ``feed_date``. Values without an offset are UTC by feed contract.
    """
    text = value.strip()
    day = feed_date or PLACEHOLDER_DATE
    m = _TIME_ONLY.match(text)
    if m:
        ymd, hms, zone = (day.year, day.month, day.day), m.groups(), None
    else:
        m = _DATETIME.match(text)
        if not m:
            return None, f"not an ISO 8601 date-time or HH:MM:SS: {value!r}"
        groups = m.groups()
        ymd, hms, zone = tuple(int(g) for g in groups[:3]), groups[3:7], groups[7]
    hour, minute, second, fraction = hms
    try:
        parsed = datetime(
            *ymd, int(hour), int(minute), int(second), int((fraction or "0")[:6].ljust(6, "0")), timezone.utc
        )
        if zone and zone.upper() != "Z":
            hours, minutes = int(zone[1:3]), int(zone[4:6])
            if hours > 23 or minutes > 59:
                raise ValueError(f"invalid UTC offset {zone}")
            sign = 1 if zone[0] == "+" else -1
            parsed -= sign * timedelta(hours=hours, minutes=minutes)
    except (ValueError, OverflowError) as exc:
        return None, f"{value!r}: {exc}"
    if not _MIN_YEAR <= parsed.year <= _MAX_YEAR:
        return None, f"{value!r}: outside {_MIN_YEAR}-{_MAX_YEAR}"
    return parsed, None


def parse_amount(value: str) -> tuple[Decimal | None, str | None]:
    text = value.strip()
    # Decimal() alone would also accept "1_000", "Infinity", "NaN" and non-ASCII digits.
    if not _NUMBER.match(text):
        return None, f"not a number: {value!r}"
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None, f"not a number: {value!r}"
    if amount <= 0:
        return None, f"must be positive: {value!r}"
    if amount.adjusted() >= _MAX_INTEGER_DIGITS:
        return None, f"larger than uint256: {value!r}"
    with localcontext() as ctx:
        ctx.prec = AMOUNT_PRECISION
        if -amount.normalize().as_tuple().exponent > _MAX_FRACTION_DIGITS:
            return None, f"more than {_MAX_FRACTION_DIGITS} decimal places: {value!r}"
    return amount, None


def format_amount(amount: Decimal) -> str:
    """Canonical plain notation: 1.2E+5 and 120000.00 both become 120000."""
    with localcontext() as ctx:
        ctx.prec = AMOUNT_PRECISION
        return format(amount.normalize(), "f")


BlockTimeResolver = Callable[[str], Optional[datetime]]


def parse_event(
    raw: RawRow,
    feed_date: date | None = None,
    resolve_block_time: BlockTimeResolver | None = None,
) -> TradeEvent:
    """Build a TradeEvent. Every field problem becomes a REJECT issue on the event.

    ``resolve_block_time`` looks a tx_hash up in an authoritative source (a node
    RPC in production). When it returns a value, a missing block_time is
    backfilled and the event carries a ``block_time_backfilled`` flag.
    """
    ev = TradeEvent(raw=raw)
    f = raw.fields

    if raw.overflow:
        ev.add("malformed_row", REJECT, f"{len(raw.overflow)} value(s) beyond the header: {raw.overflow}")

    required = list(REQUIRED_COLUMNS)
    if LOG_INDEX_COLUMN in f:
        required.append(LOG_INDEX_COLUMN)
    missing = [c for c in required if is_null(f.get(c))]
    if "block_time" in missing and resolve_block_time and not is_null(f.get("tx_hash")):
        resolved = resolve_block_time(normalize_id(f["tx_hash"]))
        if resolved is not None:
            missing.remove("block_time")
            ev.block_time = resolved
            ev.add(
                "block_time_backfilled",
                FLAG,
                f"block_time was null, taken from chain: {resolved.isoformat()}",
            )
    if missing:
        ev.add("missing_required_field", REJECT, f"null or empty: {', '.join(missing)}")

    if not is_null(f.get("event_id")):
        ev.event_id = f["event_id"].strip()
    if not is_null(f.get("tx_hash")):
        ev.tx_hash = normalize_id(f["tx_hash"])
    if not is_null(f.get("wallet")):
        ev.wallet = normalize_id(f["wallet"])

    if not is_null(f.get("side")):
        side = f["side"].strip().upper()
        if side in SIDES:
            ev.side = side
        else:
            ev.add("invalid_side", REJECT, f"expected BUY or SELL, got {f['side']!r}")

    if not is_null(f.get("amount")):
        ev.amount, err = parse_amount(f["amount"])
        if err:
            ev.add("invalid_amount", REJECT, err)

    stamps = [f.get(c) for c in ("block_time", "ingested_at") if not is_null(f.get(c))]
    if len({is_time_only(v) for v in stamps}) > 1:
        ev.add("mixed_timestamp_formats", REJECT, "one timestamp has a date, the other is time-only")
    for column in ("block_time", "ingested_at"):
        if not is_null(f.get(column)):
            value, err = parse_timestamp(f[column], feed_date)
            if err:
                ev.add("invalid_timestamp", REJECT, f"{column}: {err}")
            setattr(ev, column, value)

    if not is_null(f.get(LOG_INDEX_COLUMN)):
        text = f[LOG_INDEX_COLUMN].strip()
        if _UNSIGNED_INT.match(text):
            ev.log_index = int(text)
        else:
            ev.add("invalid_log_index", REJECT, f"expected a non-negative integer, got {text!r}")

    return ev
