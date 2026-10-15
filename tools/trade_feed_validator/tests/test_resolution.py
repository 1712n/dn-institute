from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from mocks import EVT_003_TRADE, EVT_007_TRADE, MockChainResolver, trade, utc

from trade_feed_validator.models import DropReason, Flag, Reason
from trade_feed_validator.parsing import COLUMNS
from trade_feed_validator.pipeline import Validator
from trade_feed_validator.resolution import NoOpResolver, TxLookup, resolve

SAMPLE = Path(__file__).parent.parent / "sample_feed.csv"


def run(chain, rows=None):
    validator = Validator()
    validated = validator.validate_file(SAMPLE) if rows is None else validator.validate(rows)
    return validated, resolve(validated.quarantined, chain, validator)


def by_id(events):
    return {e.event_id: e for e in events}


def dropped(resolved):
    return {d.row.raw["event_id"]: d.reason for d in resolved.dropped}


def row(event_id, block_time="2026-01-01T09:00:00Z", ingested_at="2026-01-01T09:00:03Z"):
    values = {
        "event_id": event_id,
        "tx_hash": "0xbb1",
        "block_time": block_time,
        "wallet": "0xD4…",
        "side": "BUY",
        "amount": "100",
        "ingested_at": ingested_at,
    }
    return {c: values[c] for c in COLUMNS}


# The trade behind every row built by `row`.
ROW_TRADE = trade("0xbb1", "0xD4…", "BUY", "100")


def test_noop_resolver_keeps_every_row_quarantined():
    validated, resolved = run(NoOpResolver())
    assert resolved.loaded == [] and resolved.dropped == []
    assert resolved.quarantined == validated.quarantined


def test_backfill_fills_block_time_from_chain():
    _, resolved = run(MockChainResolver(txs={"0xaa4": utc(9, 58, 20)}))
    evt = by_id(resolved.loaded)["evt_005"]
    assert evt.block_time == utc(9, 58, 20)
    assert evt.flags == {Flag.BLOCK_TIME_BACKFILLED}


def test_backfill_drops_row_when_tx_is_not_on_chain():
    _, resolved = run(MockChainResolver(txs={"0xaa4": None}))
    assert dropped(resolved) == {"evt_005": DropReason.TX_NOT_FOUND}


def test_backfilled_row_is_rechecked_for_duplicates():
    rows = [(2, row("evt_a")), (3, row("evt_b", block_time=""))]
    _, resolved = run(MockChainResolver(txs={"0xbb1": utc(9, 0, 0)}), rows)
    [held] = resolved.quarantined
    assert held.reasons == (Reason.SUSPECTED_DUPLICATE,)
    assert held.event.block_time == utc(9, 0, 0)
    assert held.event.flags == {Flag.BLOCK_TIME_BACKFILLED}


def test_backfilled_duplicate_is_loaded_when_the_chain_confirms_a_separate_trade():
    rows = [(2, row("evt_a")), (3, row("evt_b", block_time=""))]
    _, resolved = run(MockChainResolver(txs={"0xbb1": utc(9, 0, 0)}, trades={ROW_TRADE: 2}), rows)
    assert resolved.quarantined == [] and resolved.dropped == []
    [loaded] = resolved.loaded
    assert loaded.event_id == "evt_b"
    assert loaded.block_time == utc(9, 0, 0)
    assert loaded.flags == {Flag.BLOCK_TIME_BACKFILLED, Flag.CONFIRMED_DISTINCT_TRADE}


def test_second_backfilled_row_of_a_trade_is_a_duplicate_of_the_first():
    rows = [(2, row("evt_a", block_time="")), (3, row("evt_b", block_time=""))]
    _, resolved = run(MockChainResolver(txs={"0xbb1": utc(9, 0, 0)}, trades={ROW_TRADE: 1}), rows)
    assert resolved.quarantined == []
    [loaded] = resolved.loaded
    assert (loaded.event_id, loaded.flags) == ("evt_a", {Flag.BLOCK_TIME_BACKFILLED})
    assert dropped(resolved) == {"evt_b": DropReason.DUPLICATE_CONFIRMED}


def test_backfilled_row_with_ingest_before_chain_time_flags_ingested_at():
    _, resolved = run(MockChainResolver(txs={"0xaa4": utc(9, 59, 0)}))
    assert by_id(resolved.loaded)["evt_005"].flags == {
        Flag.BLOCK_TIME_BACKFILLED,
        Flag.INGESTED_AT_UNRELIABLE,
    }


def test_duplicate_is_dropped_when_chain_has_one_matching_trade():
    _, resolved = run(MockChainResolver(trades={EVT_003_TRADE: 1}))
    assert dropped(resolved) == {"evt_003": DropReason.DUPLICATE_CONFIRMED}


def test_duplicate_is_loaded_when_chain_has_two_matching_trades():
    _, resolved = run(MockChainResolver(trades={EVT_007_TRADE: 2}))
    assert by_id(resolved.loaded)["evt_007"].flags == {Flag.CONFIRMED_DISTINCT_TRADE}


def test_only_records_beyond_the_chain_count_are_dropped():
    rows = [(2, row("evt_a")), (3, row("evt_b")), (4, row("evt_c"))]
    _, resolved = run(MockChainResolver(trades={ROW_TRADE: 2}), rows)
    assert list(by_id(resolved.loaded)) == ["evt_b"]
    assert dropped(resolved) == {"evt_c": DropReason.DUPLICATE_CONFIRMED}


@pytest.mark.parametrize(
    "other_trade",
    [
        trade("0xaa2", "0xE5…", "BUY", "120000"),
        trade("0xaa2", "0xD4…", "SELL", "120000"),
        trade("0xaa2", "0xD4…", "BUY", "1"),
    ],
    ids=["other wallet", "other side", "other amount"],
)
def test_duplicate_count_is_asked_for_the_rows_own_trade(other_trade):
    _, resolved = run(MockChainResolver(trades={other_trade: 1}))
    assert resolved.dropped == []
    assert "evt_003" in {q.raw["event_id"] for q in resolved.quarantined}


def test_duplicate_is_dropped_when_chain_has_no_such_trade():
    _, resolved = run(MockChainResolver(trades={EVT_003_TRADE: 0}))
    assert dropped(resolved) == {"evt_003": DropReason.DUPLICATE_CONFIRMED}


def test_corrected_row_is_matched_for_duplicates_on_its_chain_time():
    impossible = row("evt_b", block_time="2026-01-01T09:10:00Z")
    rows = [(2, row("evt_a")), (3, impossible)]
    _, resolved = run(MockChainResolver(txs={"0xbb1": utc(9, 0, 0)}, trades={ROW_TRADE: 1}), rows)
    assert dropped(resolved) == {"evt_b": DropReason.DUPLICATE_CONFIRMED}


def test_verified_block_time_loads_with_ingested_at_flagged():
    _, resolved = run(MockChainResolver(txs={"0xaa6": utc(10, 10, 0)}))
    evt = by_id(resolved.loaded)["evt_008"]
    assert evt.block_time == utc(10, 10, 0)
    assert evt.flags == {Flag.INGESTED_AT_UNRELIABLE}


def test_wrong_block_time_is_corrected_from_chain():
    _, resolved = run(MockChainResolver(txs={"0xaa6": utc(9, 59, 40)}))
    evt = by_id(resolved.loaded)["evt_008"]
    assert evt.block_time == utc(9, 59, 40)
    assert evt.flags == {Flag.BLOCK_TIME_CORRECTED}


def test_corrected_block_time_still_after_ingest_flags_both():
    _, resolved = run(MockChainResolver(txs={"0xaa6": utc(10, 5, 0)}))
    assert by_id(resolved.loaded)["evt_008"].flags == {
        Flag.BLOCK_TIME_CORRECTED,
        Flag.INGESTED_AT_UNRELIABLE,
    }


def test_impossible_timestamp_is_dropped_when_tx_is_not_on_chain():
    _, resolved = run(MockChainResolver(txs={"0xaa6": None}))
    assert dropped(resolved) == {"evt_008": DropReason.TX_NOT_FOUND}


def test_unparseable_row_stays_quarantined():
    bad = {**row("evt_a"), "amount": "abc"}
    _, resolved = run(MockChainResolver(txs={"0xbb1": utc(9, 0, 0)}, trades={ROW_TRADE: 1}), [(2, bad)])
    [held] = resolved.quarantined
    assert held.reasons == (Reason.INVALID_AMOUNT,)


def test_sample_with_full_chain_answers_resolves_every_row():
    chain = MockChainResolver(
        txs={"0xaa4": utc(9, 58, 20), "0xaa6": utc(10, 10, 0)},
        trades={EVT_003_TRADE: 1, EVT_007_TRADE: 2},
    )
    validated, resolved = run(chain)
    assert resolved.quarantined == []
    assert dropped(resolved) == {"evt_003": DropReason.DUPLICATE_CONFIRMED}
    loaded = validated.clean + resolved.loaded
    assert sorted(e.event_id for e in loaded) == [f"evt_00{i}" for i in (1, 2, 4, 5, 6, 7, 8)]
    assert sum(e.amount for e in loaded) == Decimal("585000")


def test_resolver_time_is_converted_to_utc():
    plus_two = datetime(2026, 1, 1, 11, 58, 20, tzinfo=timezone(timedelta(hours=2)))
    _, resolved = run(MockChainResolver(txs={"0xaa4": plus_two}))
    assert by_id(resolved.loaded)["evt_005"].block_time == utc(9, 58, 20)
    assert by_id(resolved.loaded)["evt_005"].block_time.tzinfo == UTC


def test_resolver_time_without_timezone_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        TxLookup(datetime(2026, 1, 1, 9, 58, 20))
