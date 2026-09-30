from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from validator import Config, ConfigError, Status, TradeFeedValidator

FEED_DATE = date(2026, 9, 28)
CONFIG = Config(feed_date=FEED_DATE)


def event(**overrides):
    record = {
        "event_id": "evt_1",
        "tx_hash": "0xaa1",
        "block_time": "09:00:00",
        "wallet": "0xd4",
        "side": "BUY",
        "amount": "100",
        "ingested_at": "09:00:03",
    }
    record.update(overrides)
    return record


def run(*records, config=CONFIG):
    validator = TradeFeedValidator(config)
    return [validator.process(r) for r in records]


# --- field validation -------------------------------------------------------


@pytest.mark.parametrize("token", ["null", "NULL", "", "  ", "None"])
def test_missing_value_tokens_are_dead_lettered(token):
    [outcome] = run(event(block_time=token))
    assert outcome.status is Status.DEAD_LETTER
    assert outcome.reasons == ("missing_block_time",)


def test_absent_column_counts_as_missing():
    record = event()
    del record["wallet"]
    [outcome] = run(record)
    assert outcome.reasons == ("missing_wallet",)


def test_all_field_errors_are_reported_together():
    [outcome] = run(event(event_id="null", amount="-5", side="HOLD", ingested_at="soon"))
    assert set(outcome.reasons) == {"missing_event_id", "invalid_amount", "invalid_side", "invalid_ingested_at"}


@pytest.mark.parametrize("amount", ["abc", "-5", "+5", "0", "0.0", "NaN", "inf", "1,000", "1_000", "1e100"])
def test_invalid_amounts(amount):
    [outcome] = run(event(amount=amount))
    assert outcome.reasons == ("invalid_amount",)


def test_amount_forms_are_normalised_for_comparison():
    first, second = run(event(amount="1.5e3"), event(event_id="evt_2", amount="1500.00"))
    assert first.trade.amount == Decimal(1500)
    assert second.status is Status.DUPLICATE


def test_side_is_case_and_whitespace_insensitive():
    [outcome] = run(event(side=" sell "))
    assert outcome.trade.side == "SELL"


def test_iso_timestamps_are_normalised_to_utc():
    [outcome] = run(event(block_time="2026-09-28T11:00:00+02:00", ingested_at="2026-09-28T09:00:03Z"))
    assert outcome.status is Status.ACCEPTED
    assert outcome.trade.block_time == datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc)


def test_timestamp_without_offset_is_ambiguous():
    [outcome] = run(event(block_time="2026-09-28T09:00:00"))
    assert outcome.reasons == ("invalid_block_time",)


@pytest.mark.parametrize("value", ["25:00:00", "0001-01-01T00:00:00+01:00", "yesterday"])
def test_unparseable_timestamps(value):
    [outcome] = run(event(block_time=value))
    assert outcome.reasons == ("invalid_block_time",)


def test_time_only_timestamps_require_a_feed_date():
    with pytest.raises(ConfigError):
        run(event(), config=Config())


def test_strict_identifiers_reject_shortened_ids():
    config = Config(feed_date=FEED_DATE, strict_identifiers=True)
    [short] = run(event(), config=config)
    assert set(short.reasons) == {"invalid_tx_hash", "invalid_wallet"}
    [full] = run(event(tx_hash="0x" + "ab" * 32, wallet="0x" + "cd" * 20), config=config)
    assert full.status is Status.ACCEPTED


# --- time consistency -------------------------------------------------------


def test_block_time_after_ingestion_is_dead_lettered():
    [outcome] = run(event(block_time="10:10:00", ingested_at="09:59:50"))
    assert outcome.reasons == ("block_time_after_ingestion",)


def test_small_clock_skew_is_tolerated():
    [outcome] = run(event(block_time="09:00:10", ingested_at="09:00:00"))
    assert outcome.status is Status.ACCEPTED


def test_epoch_placeholder_block_time_is_dead_lettered():
    [outcome] = run(event(block_time="1970-01-01T00:00:00Z"))
    assert "block_time_before_min" in outcome.reasons


def test_ingestion_in_the_future_is_dead_lettered():
    config = Config(feed_date=FEED_DATE, now=datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc))
    [outcome] = run(event(), config=config)
    assert outcome.reasons == ("ingested_at_in_future",)


def test_high_ingestion_lag_is_flagged_not_rejected():
    [outcome] = run(event(ingested_at="09:05:00"))
    assert outcome.status is Status.ACCEPTED
    assert outcome.flags == ("high_ingestion_lag",)


def test_out_of_chain_order_arrival_is_flagged():
    newer, older = run(
        event(block_time="09:10:00", ingested_at="09:10:02"),
        event(event_id="evt_2", tx_hash="0xaa2", block_time="09:05:00", ingested_at="09:05:03"),
    )
    assert newer.flags == ()
    assert older.status is Status.ACCEPTED
    assert older.flags == ("late_arrival",)


# --- identity and duplicates ------------------------------------------------


def test_redelivery_under_new_event_id_is_a_duplicate():
    # Sample rows 2-3: same trade, new event_id, arrives minutes later.
    first, retry = run(event(event_id="evt_002"), event(event_id="evt_003", ingested_at="09:02:41"))
    assert first.status is Status.ACCEPTED
    assert retry.status is Status.DUPLICATE
    assert retry.reasons == ("duplicate_trade",)
    assert retry.related_event == "evt_002"


def test_identical_twins_keep_the_first_arrival():
    # Sample rows 6-7: every field but event_id identical, including ingested_at.
    first, twin = run(event(event_id="evt_006"), event(event_id="evt_007"))
    assert (first.status, twin.status) == (Status.ACCEPTED, Status.DUPLICATE)
    assert twin.related_event == "evt_006"


def test_replayed_event_id_is_a_duplicate():
    first, replay = run(event(), event(ingested_at="09:30:00"))
    assert replay.status is Status.DUPLICATE
    assert replay.reasons == ("duplicate_event_id",)


def test_same_wallet_side_amount_in_another_tx_is_not_a_duplicate():
    # Sample rows 1-2: identical wallet, side and amount, but distinct transactions.
    outcomes = run(
        event(event_id="evt_001"),
        event(event_id="evt_002", tx_hash="0xaa2", block_time="09:27:18", ingested_at="09:27:21"),
    )
    assert [o.status for o in outcomes] == [Status.ACCEPTED, Status.ACCEPTED]


def test_distinct_legs_of_one_transaction_are_kept():
    outcomes = run(event(), event(event_id="evt_2", wallet="0xe5", side="SELL"))
    assert [o.status for o in outcomes] == [Status.ACCEPTED, Status.ACCEPTED]


def test_event_id_reused_for_another_trade_is_a_conflict():
    first, reused = run(event(), event(tx_hash="0xbb1", amount="999"))
    assert reused.status is Status.DEAD_LETTER
    assert reused.reasons == ("conflicting_event_id",)


def test_duplicate_event_id_is_reserved():
    _, dup, reused = run(
        event(event_id="evt_1"),
        event(event_id="evt_2"),
        event(event_id="evt_2", tx_hash="0xbb1"),
    )
    assert dup.status is Status.DUPLICATE
    assert reused.reasons == ("conflicting_event_id",)


def test_same_transaction_in_another_block_is_a_conflict_not_a_duplicate():
    first, moved = run(event(), event(event_id="evt_2", block_time="09:00:12", ingested_at="09:00:15"))
    assert moved.status is Status.DEAD_LETTER
    assert moved.reasons == ("conflicting_block_time",)
    assert moved.related_event == "evt_1"


def test_identifier_case_does_not_defeat_deduplication():
    first, upper = run(event(tx_hash="0xabc", wallet="0xd4"), event(event_id="evt_2", tx_hash="0xABC", wallet="0xD4"))
    assert upper.status is Status.DUPLICATE


def test_log_index_distinguishes_identical_fills():
    outcomes = run(event(log_index="0"), event(event_id="evt_2", log_index="1"))
    assert [o.status for o in outcomes] == [Status.ACCEPTED, Status.ACCEPTED]


def test_same_log_with_different_payload_is_a_conflict():
    first, changed = run(event(log_index="3"), event(event_id="evt_2", log_index="3", amount="101"))
    assert changed.reasons == ("conflicting_payload",)
    assert changed.related_event == "evt_1"


def test_invalid_log_index():
    [outcome] = run(event(log_index="-1"))
    assert outcome.reasons == ("invalid_log_index",)


def test_dead_letter_does_not_reserve_identity_so_repairs_can_be_replayed():
    # evt_005: dead-lettered for a missing block_time, then replayed once repaired.
    validator = TradeFeedValidator(CONFIG)
    broken = validator.process(event(event_id="evt_005", block_time="null"))
    repaired = validator.process(event(event_id="evt_005", block_time="08:58:20"))
    assert broken.status is Status.DEAD_LETTER
    assert repaired.status is Status.ACCEPTED


# --- bounded state ----------------------------------------------------------


def iso(minutes):
    return (datetime(2026, 9, 28, tzinfo=timezone.utc) + timedelta(minutes=minutes)).isoformat()


def test_state_is_bounded_by_the_dedup_horizon():
    validator = TradeFeedValidator(Config(dedup_horizon=timedelta(minutes=10)))
    for i in range(1000):
        validator.process(event(event_id=f"e{i}", tx_hash=f"0x{i:x}", block_time=iso(i), ingested_at=iso(i)))
    # Three indexes, one entry each per trade within the 10-minute horizon.
    assert validator.state_size <= 3 * 11


def test_event_older_than_the_dedup_horizon_is_dead_lettered():
    validator = TradeFeedValidator(Config(dedup_horizon=timedelta(minutes=10)))
    validator.process(event(block_time=iso(0), ingested_at=iso(0)))
    validator.process(event(event_id="evt_2", tx_hash="0xbb", block_time=iso(60), ingested_at=iso(60)))
    # Could be a copy of evt_1, whose state has been evicted: never accept blindly.
    stale = validator.process(event(event_id="evt_3", block_time=iso(0), ingested_at=iso(61)))
    assert stale.reasons == ("beyond_dedup_horizon",)
