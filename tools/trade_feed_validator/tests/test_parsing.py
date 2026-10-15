from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from trade_feed_validator.models import TIME_ONLY_DATE, Reason, Side
from trade_feed_validator.parsing import COLUMNS, FeedSchemaError, parse_row, read_rows

SAMPLE = Path(__file__).parent.parent / "sample_feed.csv"

VALID = {
    "event_id": "evt_001",
    "tx_hash": "0xaa1",
    "block_time": "2026-01-01T09:14:02Z",
    "wallet": "0xD4…",
    "side": "BUY",
    "amount": "120000",
    "ingested_at": "2026-01-01T09:14:05Z",
}


def parse(**overrides):
    return parse_row(2, {**VALID, **overrides})


def reasons(parsed):
    return [(v.reason, v.field) for v in parsed.violations]


def test_valid_row_parses_into_typed_event():
    parsed = parse()
    assert parsed.violations == ()
    assert parsed.event.side is Side.BUY
    assert parsed.event.amount == Decimal("120000")
    assert parsed.event.block_time == datetime(2026, 1, 1, 9, 14, 2, tzinfo=UTC)


def test_sample_feed_parses_with_only_evt_005_missing_block_time():
    parsed = [parse_row(line, raw) for line, raw in read_rows(SAMPLE)]
    assert [p.event.event_id for p in parsed] == [f"evt_00{i}" for i in range(1, 9)]
    flagged = {p.event.event_id: reasons(p) for p in parsed if p.violations}
    assert flagged == {"evt_005": [(Reason.MISSING_REQUIRED_VALUE, "block_time")]}
    assert parsed[4].event.block_time is None
    assert [p.line for p in parsed] == list(range(2, 10))


@pytest.mark.parametrize("value", ["", "  ", "null", "NULL"])
def test_missing_block_time_keeps_event_for_backfill(value):
    parsed = parse(block_time=value)
    assert reasons(parsed) == [(Reason.MISSING_REQUIRED_VALUE, "block_time")]
    assert parsed.event is not None and parsed.event.block_time is None


@pytest.mark.parametrize("column", [c for c in COLUMNS if c != "block_time"])
def test_missing_other_required_value_is_not_resolvable(column):
    parsed = parse(**{column: ""})
    assert reasons(parsed) == [(Reason.MISSING_REQUIRED_VALUE, column)]
    assert parsed.event is None


def test_fractional_amount_is_kept_exactly():
    assert parse(amount="120000.50").event.amount == Decimal("120000.50")


def test_timestamps_are_normalized_to_utc():
    parsed = parse(block_time="2026-01-01T11:14:02+02:00")
    assert parsed.event.block_time == datetime(2026, 1, 1, 9, 14, 2, tzinfo=UTC)


def test_time_of_day_is_taken_as_utc_on_a_single_day():
    parsed = parse(block_time="09:14:02", ingested_at="09:14:05")
    assert parsed.violations == ()
    assert parsed.event.block_time == datetime.combine(TIME_ONLY_DATE, time(9, 14, 2), tzinfo=UTC)
    assert parsed.event.ingested_at - parsed.event.block_time == timedelta(seconds=3)


@pytest.mark.parametrize(
    "value",
    [
        "2026-01-01 09:14:02",
        "yesterday",
        "2026-13-01T00:00:00Z",
        "0001-01-01T00:00:00+01:00",
        "9999-12-31T23:59:59-01:00",
        "9:14:02",
        "24:00:00",
        "09:14",
        "09:14:02Z",
    ],
)
def test_invalid_or_naive_timestamp_is_rejected(value):
    parsed = parse(ingested_at=value)
    assert reasons(parsed) == [(Reason.INVALID_TIMESTAMP, "ingested_at")]
    assert parsed.event is None


@pytest.mark.parametrize("value", ["buy", "HOLD", "B"])
def test_unknown_side_is_rejected(value):
    assert reasons(parse(side=value)) == [(Reason.INVALID_SIDE, "side")]


@pytest.mark.parametrize("value", ["abc", "0", "0.00", "-5", "+5", "NaN", "Infinity", "1,000", "1e5", "1e999999999"])
def test_amount_that_is_not_a_plain_positive_decimal_is_rejected(value):
    assert reasons(parse(amount=value)) == [(Reason.INVALID_AMOUNT, "amount")]


def test_all_violations_in_a_row_are_reported():
    parsed = parse(side="HOLD", amount="-1", block_time="")
    assert reasons(parsed) == [
        (Reason.MISSING_REQUIRED_VALUE, "block_time"),
        (Reason.INVALID_SIDE, "side"),
        (Reason.INVALID_AMOUNT, "amount"),
    ]
    assert parsed.event is None


def write_feed(tmp_path, text, encoding="utf-8"):
    path = tmp_path / "feed.csv"
    path.write_text(text, encoding=encoding)
    return path


def test_rows_with_wrong_field_count_are_malformed(tmp_path):
    header = ",".join(COLUMNS)
    good = ",".join(VALID.values())
    path = write_feed(tmp_path, f"{header}\n{good},extra\n{good.rsplit(',', 1)[0]}\n")
    parsed = [parse_row(line, raw) for line, raw in read_rows(path)]
    assert [reasons(p) for p in parsed] == [[(Reason.MALFORMED_ROW, None)]] * 2
    assert parsed[0].raw[None] == ["extra"]


def test_surplus_fields_do_not_collide_with_a_column_of_any_name(tmp_path):
    header = ",".join(COLUMNS) + ",_extra"
    path = write_feed(tmp_path, f"{header}\n{','.join(VALID.values())},kept,surplus\n")
    [(_, raw)] = read_rows(path)
    assert raw["_extra"] == "kept"
    assert raw[None] == ["surplus"]


def test_missing_header_column_is_fatal(tmp_path):
    path = write_feed(tmp_path, "event_id,tx_hash\nevt_001,0xaa1\n")
    with pytest.raises(FeedSchemaError, match="block_time"):
        list(read_rows(path))


def test_repeated_header_column_is_fatal(tmp_path):
    path = write_feed(tmp_path, ",".join(COLUMNS) + ",amount\n")
    with pytest.raises(FeedSchemaError, match="repeated columns: amount"):
        list(read_rows(path))


def test_byte_order_mark_is_ignored(tmp_path):
    path = write_feed(tmp_path, ",".join(COLUMNS) + "\n" + ",".join(VALID.values()) + "\n", "utf-8-sig")
    [(_, raw)] = read_rows(path)
    assert parse_row(2, raw).violations == ()
