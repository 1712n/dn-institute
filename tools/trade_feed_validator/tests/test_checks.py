from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from trade_feed_validator.checks import DuplicateIndex, check_invariants
from trade_feed_validator.models import Reason, Side, TradeEvent
from trade_feed_validator.parsing import parse_row, read_rows

SAMPLE = Path(__file__).parent.parent / "sample_feed.csv"

EVENT = TradeEvent(
    event_id="evt_a",
    tx_hash="0xaa1",
    block_time=datetime(2026, 1, 1, 9, 0, 0, tzinfo=timezone.utc),
    wallet="0xD4…",
    side=Side.BUY,
    amount=Decimal("100"),
    ingested_at=datetime(2026, 1, 1, 9, 0, 3, tzinfo=timezone.utc),
)


@pytest.fixture
def sample():
    return {p.event.event_id: p.event for p in (parse_row(*r) for r in read_rows(SAMPLE))}


def test_sample_duplicates_are_the_later_record_of_each_pair(sample):
    index = DuplicateIndex()
    found = {e.event_id: v.detail for e in sample.values() for v in index.check(e)}
    assert found == {"evt_003": "same trade as evt_002", "evt_007": "same trade as evt_006"}


def test_sample_invariant_violation_is_evt_008(sample):
    found = {e.event_id: check_invariants(e) for e in sample.values() if check_invariants(e)}
    assert list(found) == ["evt_008"]
    [violation] = found["evt_008"]
    assert violation.reason is Reason.INGESTED_BEFORE_BLOCK
    assert violation.detail == "ingested 0:10:10 before block_time"


def test_same_wallet_side_amount_in_different_transactions_is_not_a_duplicate(sample):
    index = DuplicateIndex()
    assert index.check(sample["evt_001"]) == []
    assert index.check(sample["evt_002"]) == []


def test_wallet_buying_then_selling_is_not_a_duplicate(sample):
    index = DuplicateIndex()
    assert index.check(sample["evt_006"]) == []
    assert index.check(sample["evt_008"]) == []


@pytest.mark.parametrize(
    "change",
    [
        {"tx_hash": "0xaa2"},
        {"wallet": "0xE5…"},
        {"side": Side.SELL},
        {"amount": Decimal("101")},
        {"block_time": EVENT.block_time + timedelta(seconds=1)},
    ],
)
def test_any_differing_trade_value_means_a_different_trade(change):
    index = DuplicateIndex()
    index.check(EVENT)
    assert index.check(replace(EVENT, event_id="evt_b", **change)) == []


def test_equal_amounts_match_regardless_of_notation():
    index = DuplicateIndex()
    index.check(EVENT)
    assert index.check(replace(EVENT, event_id="evt_b", amount=Decimal("100.00")))


def test_repeat_with_the_same_event_id_is_flagged():
    index = DuplicateIndex()
    index.check(EVENT)
    [violation] = index.check(EVENT)
    assert violation.detail == "same trade as evt_a"


def test_every_later_match_points_to_the_first_record():
    index = DuplicateIndex()
    index.check(EVENT)
    details = [index.check(replace(EVENT, event_id=f"evt_{i}"))[0].detail for i in range(3)]
    assert details == ["same trade as evt_a"] * 3


def test_event_without_block_time_is_not_matched_or_registered():
    index = DuplicateIndex()
    pending = replace(EVENT, block_time=None)
    assert index.check(pending) == []
    assert index.check(pending) == []
    assert index.check(EVENT) == []


def test_ingested_at_equal_to_block_time_is_valid():
    assert check_invariants(replace(EVENT, ingested_at=EVENT.block_time)) == []


def test_missing_block_time_has_no_invariant_to_check():
    assert check_invariants(replace(EVENT, block_time=None)) == []

