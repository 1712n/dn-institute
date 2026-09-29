"""One test per data-quality issue in the sample feed from the challenge."""

from datetime import datetime, timezone

from pipeline import ACCEPTED, DEAD_LETTER, DUPLICATE
from tests.support import SAMPLE, by_id, codes, run_csv


def test_every_row_gets_exactly_one_outcome(sample):
    assert {e.event_id: sample.outcome[e.row] for e in sample.events} == {
        "evt_001": ACCEPTED,
        "evt_002": ACCEPTED,
        "evt_003": DUPLICATE,
        "evt_004": ACCEPTED,
        "evt_005": DEAD_LETTER,
        "evt_006": ACCEPTED,
        "evt_007": DUPLICATE,
        "evt_008": DEAD_LETTER,
    }


def test_volume_naive_vs_clean_vs_quarantined(sample):
    volume = sample.volume()
    assert volume == {"naive": "705000", "clean": "375000", "dead_letter": "120000", "duplicate": "210000"}


def test_redelivery_under_new_event_id_is_dropped(sample):
    """Rows 2-3: tx 0xaa2 delivered twice, the retry 2m38s later with a new event_id."""
    evt_003 = by_id(sample, "evt_003")
    assert sample.duplicate_of[evt_003.row] == "evt_002"
    assert "redelivered 2m38s later" in next(i.detail for i in evt_003.issues if i.code == "duplicate_trade")
    assert "high_ingest_lag" in codes(evt_003)  # the retry is also visible as ingest lag


def test_double_emission_is_dropped(sample):
    """Rows 6-7: identical in every field except event_id."""
    evt_007 = by_id(sample, "evt_007")
    assert sample.duplicate_of[evt_007.row] == "evt_006"
    assert "emitted twice within one second" in next(
        i.detail for i in evt_007.issues if i.code == "duplicate_trade"
    )


def test_missing_block_time_is_dead_lettered_with_raw_row(sample):
    """Row 5: block_time is null. Quarantined, never dropped and never guessed."""
    evt_005 = by_id(sample, "evt_005")
    assert sample.outcome[evt_005.row] == DEAD_LETTER
    assert codes(evt_005) == {"missing_required_field"}
    assert evt_005.raw.fields["block_time"] == "null"  # kept verbatim for replay


def test_ingested_before_block_time_is_dead_lettered(sample):
    """Row 8: ingested 10m10s before its block was produced."""
    evt_008 = by_id(sample, "evt_008")
    assert sample.outcome[evt_008.row] == DEAD_LETTER
    assert "ingested_before_block_time" in codes(evt_008)


def test_ingest_clock_points_at_the_wrong_field(sample):
    """Row 8's block_time fits chain order, its ingested_at runs backwards vs. rows 6-7.
    The flag records which of the two timestamps is the likely culprit."""
    evt_008 = by_id(sample, "evt_008")
    assert "ingest_clock_regression" in codes(evt_008)
    assert "late_arrival" not in codes(evt_008)


def test_round_trip_by_same_wallet_is_flagged(sample):
    """0xF6 buys 90000 (evt_006) and sells 90000 (evt_008) 6m49s later."""
    assert [(a.event_id, b.event_id) for a, b in sample.round_trips] == [("evt_006", "evt_008")]
    assert "round_trip_suspect" in codes(by_id(sample, "evt_006"))
    assert "round_trip_suspect" in codes(by_id(sample, "evt_008"))


def test_same_wallet_same_amount_in_different_tx_is_not_a_duplicate(sample):
    """Rows 1-2: 0xD4 buys 120000 twice in different transactions. Both are real."""
    assert sample.outcome[by_id(sample, "evt_001").row] == ACCEPTED
    assert sample.outcome[by_id(sample, "evt_002").row] == ACCEPTED


def test_clean_rows_carry_no_issues(sample):
    for event_id in ("evt_001", "evt_002", "evt_004"):
        assert by_id(sample, event_id).issues == []


def test_accepted_output_is_in_chain_order(sample):
    times = [e.block_time for e in sample.accepted]
    assert times == sorted(times)


def test_time_only_timestamps_raise_a_feed_warning(sample):
    assert any("time-only timestamps" in w for w in sample.warnings)


def test_backfill_from_chain_repairs_evt_005():
    chain = {"0xaa4": datetime(2026, 9, 28, 9, 58, 1, tzinfo=timezone.utc)}
    result = run_csv(SAMPLE.read_text(encoding="utf-8"), resolver=chain.get)
    evt_005 = by_id(result, "evt_005")
    assert result.outcome[evt_005.row] == ACCEPTED
    assert codes(evt_005) == {"block_time_backfilled"}
    assert evt_005.block_time == chain["0xaa4"]
    assert result.volume()["clean"] == "405000"
