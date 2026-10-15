from decimal import Decimal
from pathlib import Path

import pytest

from trade_feed_validator.models import Reason
from trade_feed_validator.parsing import COLUMNS
from trade_feed_validator.pipeline import Validator

SAMPLE = Path(__file__).parent.parent / "sample_feed.csv"


def row(event_id, tx_hash="0xaa1", block_time="2026-01-01T09:00:00Z", ingested_at="2026-01-01T09:00:03Z", **rest):
    values = {
        "event_id": event_id,
        "tx_hash": tx_hash,
        "block_time": block_time,
        "wallet": "0xD4…",
        "side": "BUY",
        "amount": "100",
        "ingested_at": ingested_at,
        **rest,
    }
    return {c: values[c] for c in COLUMNS}


# The data-quality issues in the sample, as named in the README, with the rows
# each one affects and the reason they're quarantined with.
SAMPLE_ISSUES = {
    "duplicate events": {"evt_003": Reason.SUSPECTED_DUPLICATE, "evt_007": Reason.SUSPECTED_DUPLICATE},
    "missing required value": {"evt_005": Reason.MISSING_REQUIRED_VALUE},
    "invariant violation": {"evt_008": Reason.INGESTED_BEFORE_BLOCK},
}


@pytest.mark.parametrize("issue", SAMPLE_ISSUES)
def test_sample_issue_is_caught(issue):
    result = Validator().validate_file(SAMPLE)
    reasons = {q.raw["event_id"]: q.reasons for q in result.quarantined}
    for event_id, reason in SAMPLE_ISSUES[issue].items():
        assert reasons[event_id] == (reason,)


def test_sample_rows_without_issues_are_clean():
    result = Validator().validate_file(SAMPLE)
    assert [e.event_id for e in result.clean] == ["evt_001", "evt_002", "evt_004", "evt_006"]
    assert len(result.quarantined) == sum(len(rows) for rows in SAMPLE_ISSUES.values())


def test_no_volume_is_lost_between_clean_and_quarantine():
    result = Validator().validate_file(SAMPLE)
    clean = sum(e.amount for e in result.clean)
    held = sum(q.event.amount for q in result.quarantined)
    assert (clean, held) == (Decimal("375000"), Decimal("330000"))
    assert clean + held == Decimal("705000")


def test_quarantine_keeps_the_raw_row_line_and_parsed_event():
    rows = [(2, row("evt_a")), (3, row("evt_b"))]
    [held] = Validator().validate(rows).quarantined
    assert held.line == 3
    assert held.raw == row("evt_b")
    assert held.event.event_id == "evt_b"
    assert held.violations[0].detail == "same trade as evt_a"


def test_unparseable_row_is_quarantined_and_the_run_continues():
    rows = [(2, row("evt_a", amount="abc")), (3, row("evt_b", tx_hash="0xaa2"))]
    result = Validator().validate(rows)
    assert [e.event_id for e in result.clean] == ["evt_b"]
    [held] = result.quarantined
    assert held.reasons == (Reason.INVALID_AMOUNT,)
    assert held.event is None


def test_row_with_impossible_block_time_is_also_matched_for_duplicates():
    impossible = {"block_time": "2026-01-01T09:10:00Z", "ingested_at": "2026-01-01T09:00:03Z"}
    rows = [(2, row("evt_a")), (3, row("evt_b", **impossible))]
    result = Validator().validate(rows)
    assert [e.event_id for e in result.clean] == ["evt_a"]
    [held] = result.quarantined
    assert held.reasons == (Reason.INGESTED_BEFORE_BLOCK, Reason.SUSPECTED_DUPLICATE)


def test_empty_feed_gives_empty_result():
    result = Validator().validate([])
    assert result.clean == [] and result.quarantined == []
