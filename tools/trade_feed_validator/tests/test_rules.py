"""Edge cases that the sample does not contain but a real indexer feed will."""

from datetime import datetime, timedelta, timezone

import pytest

from pipeline import ACCEPTED, DEAD_LETTER, DUPLICATE
from rules import Config
from tests.support import HEADER, by_id, codes, run_rows

ROW = "{id},{tx},{bt},{wallet},{side},{amount},{ing}"


def row(id="e1", tx="0xaa1", bt="10:00:00", wallet="0xw1", side="BUY", amount="100", ing="10:00:02"):
    return ROW.format(id=id, tx=tx, bt=bt, wallet=wallet, side=side, amount=amount, ing=ing)


def outcome(result, event_id):
    return result.outcome[by_id(result, event_id).row]


# ---------------------------------------------------------------- field checks


@pytest.mark.parametrize("token", ["", "null", "NULL", "None", "NaN", "n/a"])
def test_null_tokens_are_missing(token):
    result = run_rows(row(bt=token))
    assert codes(result.events[0]) == {"missing_required_field"}


@pytest.mark.parametrize("amount", ["abc", "-5", "0", "NaN", "Infinity", "1_000", "1,000"])
def test_invalid_amounts_are_dead_lettered(amount):
    result = run_rows(row(amount=f'"{amount}"'))
    assert outcome(result, "e1") == DEAD_LETTER


def test_amounts_are_exact_decimals():
    result = run_rows(row(amount="0.1"), row(id="e2", tx="0xaa2", amount="0.2"))
    assert result.volume()["clean"] == "0.3"


@pytest.mark.parametrize("side", ["HOLD", "B", "1"])
def test_invalid_side_is_dead_lettered(side):
    assert codes(run_rows(row(side=side)).events[0]) == {"invalid_side"}


def test_side_is_case_insensitive():
    result = run_rows(row(side="buy"))
    assert result.events[0].side == "BUY" and outcome(result, "e1") == ACCEPTED


@pytest.mark.parametrize("value", ["25:00:00", "yesterday", "2026-13-01T00:00:00Z"])
def test_invalid_timestamp_is_dead_lettered(value):
    assert "invalid_timestamp" in codes(run_rows(row(bt=value)).events[0])


def test_iso_timestamps_with_offsets_are_normalized_to_utc():
    result = run_rows(row(bt="2026-09-28T13:00:00+03:00", ing="2026-09-28T10:00:02Z"))
    ev = result.events[0]
    assert ev.block_time == datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
    assert outcome(result, "e1") == ACCEPTED


def test_mixed_timestamp_formats_in_one_row_are_dead_lettered():
    result = run_rows(row(bt="10:00:00", ing="2026-09-28T10:00:02Z"))
    assert "mixed_timestamp_formats" in codes(result.events[0])


def test_mixed_timestamp_formats_across_rows_raise_a_warning():
    result = run_rows(row(), row(id="e2", tx="0xaa2", bt="2026-09-28T10:05:00Z", ing="2026-09-28T10:05:02Z"))
    assert any("mixes time-only and full" in w for w in result.warnings)


@pytest.mark.parametrize("ingested, rejected", [("09:59:55", False), ("09:59:54", True)])
def test_clock_skew_tolerance_boundary(ingested, rejected):
    result = run_rows(row(bt="10:00:00", ing=ingested))  # default skew 5s
    assert ("ingested_before_block_time" in codes(result.events[0])) is rejected


def test_ingest_lag_threshold_is_configurable():
    result = run_rows(row(ing="10:00:30"), config=Config(max_ingest_lag=timedelta(seconds=10)))
    assert "high_ingest_lag" in codes(result.events[0])
    assert outcome(result, "e1") == ACCEPTED  # a flag, not a rejection


def test_row_with_more_values_than_header_keeps_the_overflow():
    result = run_rows(row() + ",surprise")
    ev = result.events[0]
    assert outcome(result, "e1") == DEAD_LETTER
    assert ev.raw.overflow == ["surprise"]


def test_short_row_is_missing_fields():
    result = run_rows("e1,0xaa1,10:00:00")
    assert "missing_required_field" in codes(result.events[0])


# ---------------------------------------------------------------- deduplication


def test_same_event_id_redelivered_is_a_duplicate():
    result = run_rows(row(), row(ing="10:00:09"))
    assert result.outcome[2] == DUPLICATE
    assert "duplicate_event" in codes(result.events[1])


def test_event_id_reused_for_a_different_trade_is_dead_lettered():
    result = run_rows(row(), row(tx="0xbb1", amount="5"))
    assert result.outcome[2] == DEAD_LETTER
    assert "event_id_collision" in codes(result.events[1])


def test_same_trade_with_different_block_time_is_not_silently_dropped():
    """A reorg or a bad indexer re-read: one of the two block times is wrong."""
    result = run_rows(row(), row(id="e2", bt="10:00:12", ing="10:00:14"))
    assert outcome(result, "e2") == DEAD_LETTER
    assert "conflicting_duplicate" in codes(by_id(result, "e2"))


def test_different_trades_in_one_transaction_are_kept():
    """A router tx can emit several fills; only identical fills collapse."""
    result = run_rows(row(), row(id="e2", wallet="0xw2"), row(id="e3", amount="7"))
    assert [result.outcome[r] for r in (1, 2, 3)] == [ACCEPTED] * 3


def test_hex_identifiers_are_case_insensitive():
    result = run_rows(row(tx="0xAA1", wallet="0xABC"), row(id="e2", tx="0xaa1", wallet="0xabc"))
    assert outcome(result, "e2") == DUPLICATE


def test_non_hex_identifiers_stay_case_sensitive():
    """Solana-style base58 addresses differ by case."""
    result = run_rows(row(tx="5Kq", wallet="AbC"), row(id="e2", tx="5Kq", wallet="abc"))
    assert outcome(result, "e2") == ACCEPTED


def test_rejected_event_does_not_block_its_corrected_redelivery():
    result = run_rows(row(bt="null"), row())  # same event_id, block_time now present
    assert result.outcome[1] == DEAD_LETTER
    assert result.outcome[2] == ACCEPTED


def test_log_index_makes_identical_fills_distinct():
    header = HEADER + ",log_index"
    result = run_rows(row() + ",0", row(id="e2") + ",1", row(id="e3") + ",1", header=header)
    assert [result.outcome[r] for r in (1, 2, 3)] == [ACCEPTED, ACCEPTED, DUPLICATE]


def test_log_index_column_present_but_empty_is_missing():
    result = run_rows(row() + ",", header=HEADER + ",log_index")
    assert "missing_required_field" in codes(result.events[0])


# ---------------------------------------------------------------- ordering


def test_late_arrival_is_flagged_and_output_is_in_chain_order():
    result = run_rows(
        row(id="e1", tx="0x1", bt="10:05:00", ing="10:05:02"),
        row(id="e2", tx="0x2", bt="10:01:00", ing="10:05:03"),
    )
    assert "late_arrival" in codes(by_id(result, "e2"))
    assert outcome(result, "e2") == ACCEPTED
    assert [e.event_id for e in result.accepted] == ["e2", "e1"]


def test_ingest_clock_regression_is_flagged():
    result = run_rows(
        row(id="e1", tx="0x1", bt="10:00:00", ing="10:10:00"),
        row(id="e2", tx="0x2", bt="10:00:00", ing="10:00:05"),
    )
    assert "ingest_clock_regression" in codes(by_id(result, "e2"))


# ---------------------------------------------------------------- round trips


def test_round_trip_outside_window_is_not_flagged():
    result = run_rows(
        row(id="e1", tx="0x1", side="BUY", bt="10:00:00", ing="10:00:01"),
        row(id="e2", tx="0x2", side="SELL", bt="10:31:00", ing="10:31:01"),
    )
    assert result.round_trips == []


def test_same_side_repeats_are_not_round_trips():
    result = run_rows(row(id="e1", tx="0x1"), row(id="e2", tx="0x2", bt="10:01:00", ing="10:01:02"))
    assert result.round_trips == []


def test_duplicates_do_not_create_extra_round_trips():
    result = run_rows(
        row(id="e1", tx="0x1", side="BUY"),
        row(id="e2", tx="0x1", side="BUY"),
        row(id="e3", tx="0x2", side="SELL", bt="10:02:00", ing="10:02:02"),
    )
    assert [(a.event_id, b.event_id) for a, b in result.round_trips] == [("e1", "e3")]


# ---------------------------------------------------------------- hostile values


@pytest.mark.parametrize(
    "value",
    ["0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00", "1900-01-01T00:00:00Z", "2026-09-28"],
)
def test_out_of_range_or_date_only_timestamps_are_dead_lettered(value):
    result = run_rows(row(bt=value))
    assert "invalid_timestamp" in codes(result.events[0])


def test_nanosecond_timestamps_are_truncated_the_same_way_on_every_python():
    result = run_rows(row(bt="2026-09-28T10:00:00.123456789Z", ing="2026-09-28T10:00:02Z"))
    assert result.events[0].block_time.microsecond == 123456


@pytest.mark.parametrize("amount", ["1e1000000", "1e78", "1e-40", "１２０"])
def test_absurd_amounts_are_dead_lettered_not_crashing(amount):
    assert "invalid_amount" in codes(run_rows(row(amount=amount)).events[0])


def test_wei_scale_amounts_add_up_exactly():
    big = "12345678901234567890123456789"
    result = run_rows(row(amount=big), row(id="e2", tx="0xaa2", amount="0.5"))
    assert result.volume()["clean"] == "12345678901234567890123456789.5"


def test_amounts_are_written_in_canonical_notation():
    result = run_rows(row(amount="1.2E+5"), row(id="e2", tx="0xaa2", amount="120000.00"))
    assert result.volume()["clean"] == "240000"


def test_non_ascii_log_index_is_dead_lettered():
    result = run_rows(row() + ",²", header=HEADER + ",log_index")
    assert "invalid_log_index" in codes(result.events[0])


# ---------------------------------------------------------------- review regressions


def test_accepted_original_is_flagged_when_a_conflicting_copy_arrives():
    result = run_rows(row(), row(id="e2", bt="10:05:00", ing="10:05:02"))
    assert "disputed_trade" in codes(by_id(result, "e1"))
    assert outcome(result, "e1") == ACCEPTED


def test_rejected_row_does_not_move_the_ingest_clock():
    result = run_rows(
        row(id="bad", tx="0x0", side="HOLD", ing="23:00:00"),
        row(id="e1", tx="0x1"),
        row(id="e2", tx="0x2", bt="10:00:05", ing="10:00:07"),
    )
    assert "ingest_clock_regression" not in codes(by_id(result, "e1"))
    assert "ingest_clock_regression" not in codes(by_id(result, "e2"))


def test_round_trip_legs_are_paired_once():
    result = run_rows(
        row(id="b1", tx="0x1", side="BUY"),
        row(id="b2", tx="0x2", side="BUY", bt="10:01:00", ing="10:01:02"),
        row(id="s1", tx="0x3", side="SELL", bt="10:02:00", ing="10:02:02"),
    )
    assert [(a.event_id, b.event_id) for a, b in result.round_trips] == [("b1", "s1")]


def test_dead_lettered_copies_do_not_create_extra_round_trips():
    """One SELL delivered twice, both copies dead-lettered, must not pair with two BUYs."""
    sell = dict(tx="0x3", side="SELL", bt="10:10:00", ing="09:59:50")
    result = run_rows(
        row(id="b1", tx="0x1"),
        row(id="b2", tx="0x2", bt="10:01:00", ing="10:01:02"),
        row(id="s1", **sell),
        row(id="s1-copy", **sell),
    )
    assert [(a.event_id, b.event_id) for a, b in result.round_trips] == [("b1", "s1")]


def test_empty_feed_raises_a_warning():
    assert any("no rows" in w for w in run_rows().warnings)


def test_same_log_with_a_different_payload_is_a_conflict_not_a_duplicate():
    header = HEADER + ",log_index"
    result = run_rows(row() + ",3", row(id="e2", side="SELL", amount="999") + ",3", header=header)
    assert "conflicting_duplicate" in codes(by_id(result, "e2"))
    assert "disputed_trade" in codes(by_id(result, "e1"))


def test_same_event_id_with_a_new_block_time_is_a_conflict_not_a_collision():
    result = run_rows(row(), row(bt="10:00:12", ing="10:00:14"))
    assert codes(result.events[1]) >= {"conflicting_duplicate"}
    assert "event_id_collision" not in codes(result.events[1])
    assert "disputed_trade" in codes(result.events[0])


def test_event_id_of_a_dropped_duplicate_cannot_be_reused():
    result = run_rows(row(), row(id="e2"), row(id="e2", tx="0xbb2", side="SELL", amount="7"))
    assert [result.outcome[r] for r in (1, 2, 3)] == [ACCEPTED, DUPLICATE, DEAD_LETTER]
    assert "event_id_collision" in codes(result.events[2])


@pytest.mark.parametrize("offset", ["+24:00", "+99:99", "-05:60"])
def test_invalid_utc_offsets_are_rejected(offset):
    result = run_rows(row(bt=f"2026-09-28T10:00:00{offset}", ing="2026-09-28T10:00:02Z"))
    assert "invalid_timestamp" in codes(result.events[0])


def test_shortened_ids_keep_their_case():
    """0xD4… is not hex, so it is not lowercased."""
    result = run_rows(row(wallet="0xD4…"))
    assert result.events[0].wallet == "0xD4…"


def test_strict_identifiers_require_full_evm_ids():
    strict = Config(strict_identifiers=True)
    full = row(tx="0x" + "a" * 64, wallet="0x" + "B" * 40)
    assert outcome(run_rows(full, config=strict), "e1") == ACCEPTED
    assert "invalid_identifier" in codes(run_rows(row(), config=strict).events[0])
    assert outcome(run_rows(row()), "e1") == ACCEPTED  # off by default


@pytest.mark.parametrize("rows", [(row(),), (row(), row(id="e2")), (row(bt="null"), row(id="e2", tx="0x2"))])
def test_every_row_read_gets_exactly_one_outcome(rows):
    result = run_rows(*rows)
    assert len(result.outcome) == len(rows) == len(result.events)
