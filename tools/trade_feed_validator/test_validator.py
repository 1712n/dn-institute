"""Tests for the trade feed validator.

Run from this folder with either:
    python3 -m unittest -v
    python3 -m pytest -v
"""

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pipeline
from validator import (
    Issue,
    Status,
    TradeFeedValidator,
    normalize_id,
    parse_timestamp,
)

HERE = Path(__file__).parent
SAMPLE = HERE / "sample_feed.csv"


def event(**overrides):
    base = {
        "event_id": "evt_x",
        "tx_hash": "0xabc",
        "block_time": "10:00:00",
        "wallet": "0xW1",
        "side": "BUY",
        "amount": "100",
        "ingested_at": "10:00:03",
    }
    base.update(overrides)
    return base


class SampleFeedTest(unittest.TestCase):
    """Every issue in the challenge's sample feed is caught."""

    @classmethod
    def setUpClass(cls):
        _, rows = pipeline.read_feed(SAMPLE)
        cls.decisions = {d.event_id: d for d in TradeFeedValidator().process_all(rows)}

    def test_clean_events_accepted_without_warnings(self):
        for event_id in ("evt_001", "evt_002", "evt_004", "evt_006"):
            d = self.decisions[event_id]
            self.assertIs(d.status, Status.ACCEPTED, event_id)
            self.assertEqual(d.issues, [], event_id)

    def test_evt_003_redelivery_is_duplicate_of_evt_002(self):
        # Same trade, new event_id, ingested ~2.5 min later (indexer retry).
        d = self.decisions["evt_003"]
        self.assertIs(d.status, Status.DUPLICATE)
        self.assertTrue(d.has(Issue.DUPLICATE_TRADE))
        self.assertEqual(d.duplicate_of, "evt_002")

    def test_evt_007_double_emit_is_duplicate_of_evt_006(self):
        # Identical to evt_006 down to ingested_at; only event_id differs.
        d = self.decisions["evt_007"]
        self.assertIs(d.status, Status.DUPLICATE)
        self.assertTrue(d.has(Issue.DUPLICATE_TRADE))
        self.assertEqual(d.duplicate_of, "evt_006")

    def test_evt_005_missing_block_time_is_dead_lettered(self):
        d = self.decisions["evt_005"]
        self.assertIs(d.status, Status.DEAD_LETTER)
        self.assertTrue(d.has(Issue.MISSING_FIELD))
        self.assertIn("block_time", str(d.issues[0]))

    def test_evt_008_ingested_before_block_time_is_dead_lettered(self):
        d = self.decisions["evt_008"]
        self.assertIs(d.status, Status.DEAD_LETTER)
        self.assertTrue(d.has(Issue.INGESTED_BEFORE_BLOCK_TIME))

    def test_evt_008_ingest_clock_went_backwards(self):
        # Arrived after evt_007 (ingested 10:03:15) but stamped 09:59:50.
        self.assertTrue(self.decisions["evt_008"].has(Issue.INGEST_CLOCK_WENT_BACKWARDS))

    def test_same_wallet_same_amount_different_tx_is_not_a_duplicate(self):
        # evt_001 and evt_002 look alike but are separate transactions.
        self.assertIs(self.decisions["evt_001"].status, Status.ACCEPTED)
        self.assertIs(self.decisions["evt_002"].status, Status.ACCEPTED)


class PipelineTest(unittest.TestCase):
    def test_end_to_end_outputs_and_volume(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                code = pipeline.main([str(SAMPLE), "--out-dir", tmp])
            self.assertEqual(code, 0)
            report = json.loads((out / "report.json").read_text())

            _, clean = pipeline.read_feed(out / "clean.csv")
            _, dupes = pipeline.read_feed(out / "duplicates.csv")
            _, dlq = pipeline.read_feed(out / "dead_letter.csv")

        self.assertEqual(
            [r["event_id"] for r in clean], ["evt_001", "evt_002", "evt_004", "evt_006"]
        )
        self.assertEqual({r["event_id"]: r["duplicate_of"] for r in dupes},
                         {"evt_003": "evt_002", "evt_007": "evt_006"})
        self.assertEqual([r["event_id"] for r in dlq], ["evt_005", "evt_008"])
        # Raw values are preserved, not reformatted.
        self.assertEqual(dlq[0]["block_time"], "null")
        # The naive pipeline overstates volume by 88%.
        self.assertEqual(report["volume_naive"], "705000")
        self.assertEqual(report["volume_validated"], "375000")

    def test_fail_on_dead_letter_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                code = pipeline.main(
                    [str(SAMPLE), "--out-dir", tmp, "--fail-on-dead-letter"]
                )
        self.assertEqual(code, 1)

    def test_clean_output_is_in_chain_order(self):
        rows = [
            event(event_id="b", tx_hash="0x2", block_time="10:05:00", ingested_at="10:05:01"),
            event(event_id="a", tx_hash="0x1", block_time="10:01:00", ingested_at="10:05:02"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            feed = Path(tmp) / "feed.csv"
            pipeline._write(feed, list(rows[0]), rows)
            pipeline.run(feed, Path(tmp) / "out")
            _, clean = pipeline.read_feed(Path(tmp) / "out" / "clean.csv")
        self.assertEqual([r["event_id"] for r in clean], ["a", "b"])
        self.assertIn("OUT_OF_ORDER", clean[0]["warnings"])


class SchemaTest(unittest.TestCase):
    def assertDeadLetter(self, raw, issue):
        d = TradeFeedValidator().process(raw)
        self.assertIs(d.status, Status.DEAD_LETTER)
        self.assertTrue(d.has(issue), d.issues)

    def test_null_spellings(self):
        for value in (None, "", "  ", "null", "NULL", "None", "NaN"):
            with self.subTest(value=value):
                self.assertDeadLetter(event(block_time=value), Issue.MISSING_FIELD)

    def test_every_required_field_is_checked(self):
        for name in event():
            with self.subTest(field=name):
                self.assertDeadLetter(event(**{name: None}), Issue.MISSING_FIELD)

    def test_invalid_side(self):
        self.assertDeadLetter(event(side="HOLD"), Issue.INVALID_SIDE)

    def test_side_is_case_insensitive(self):
        d = TradeFeedValidator().process(event(side=" sell "))
        self.assertIs(d.status, Status.ACCEPTED)
        self.assertEqual(d.event.side, "SELL")

    def test_invalid_amount(self):
        for value in ("0", "-5", "abc", "Infinity", "1e"):
            with self.subTest(value=value):
                self.assertDeadLetter(event(amount=value), Issue.INVALID_AMOUNT)

    def test_amount_is_exact_decimal(self):
        d = TradeFeedValidator().process(event(amount="0.1"))
        self.assertEqual(d.event.amount, Decimal("0.1"))

    def test_invalid_timestamp(self):
        self.assertDeadLetter(event(block_time="25:99:00"), Issue.INVALID_TIMESTAMP)
        self.assertDeadLetter(event(ingested_at="yesterday"), Issue.INVALID_TIMESTAMP)

    def test_all_errors_reported_at_once(self):
        d = TradeFeedValidator().process(event(side="X", amount="-1", block_time=None))
        self.assertEqual(
            {f.issue for f in d.issues},
            {Issue.INVALID_SIDE, Issue.INVALID_AMOUNT, Issue.MISSING_FIELD},
        )


class TimestampTest(unittest.TestCase):
    def test_formats(self):
        expected = datetime(2024, 5, 1, 9, 14, 2, tzinfo=timezone.utc)
        for value in (
            "2024-05-01T09:14:02Z",
            "2024-05-01T09:14:02",
            "2024-05-01T11:14:02+02:00",
            "1714554842",
            "1714554842000",
        ):
            with self.subTest(value=value):
                self.assertEqual(parse_timestamp(value), expected)

    def test_time_only_uses_feed_date(self):
        from datetime import date

        self.assertEqual(
            parse_timestamp("09:14:02", date(2024, 5, 1)),
            datetime(2024, 5, 1, 9, 14, 2, tzinfo=timezone.utc),
        )


class TemporalTest(unittest.TestCase):
    def test_small_clock_skew_is_tolerated(self):
        d = TradeFeedValidator().process(event(block_time="10:00:00", ingested_at="09:59:57"))
        self.assertIs(d.status, Status.ACCEPTED)

    def test_ingested_before_block_beyond_tolerance(self):
        d = TradeFeedValidator().process(event(block_time="10:00:00", ingested_at="09:59:50"))
        self.assertTrue(d.has(Issue.INGESTED_BEFORE_BLOCK_TIME))

    def test_late_arrival_warning(self):
        d = TradeFeedValidator().process(event(block_time="10:00:00", ingested_at="10:30:00"))
        self.assertIs(d.status, Status.ACCEPTED)
        self.assertTrue(d.has(Issue.LATE_ARRIVAL))

    def test_out_of_order_warning(self):
        v = TradeFeedValidator()
        v.process(event(event_id="a", tx_hash="0x1", block_time="10:05:00", ingested_at="10:05:01"))
        d = v.process(event(event_id="b", tx_hash="0x2", block_time="10:01:00", ingested_at="10:05:02"))
        self.assertIs(d.status, Status.ACCEPTED)
        self.assertTrue(d.has(Issue.OUT_OF_ORDER))

    def test_ingest_clock_small_jitter_is_tolerated(self):
        v = TradeFeedValidator()
        v.process(event(event_id="a", tx_hash="0x1", block_time="10:00:00", ingested_at="10:00:30"))
        d = v.process(event(event_id="b", tx_hash="0x2", block_time="10:00:00", ingested_at="10:00:10"))
        self.assertFalse(d.has(Issue.INGEST_CLOCK_WENT_BACKWARDS))


class DuplicateTest(unittest.TestCase):
    def test_same_event_id_same_payload(self):
        v = TradeFeedValidator()
        v.process(event())
        d = v.process(event(ingested_at="10:01:00"))
        self.assertIs(d.status, Status.DUPLICATE)
        self.assertTrue(d.has(Issue.DUPLICATE_EVENT_ID))

    def test_same_event_id_different_payload_is_conflict(self):
        v = TradeFeedValidator()
        v.process(event())
        d = v.process(event(amount="999"))
        self.assertIs(d.status, Status.DEAD_LETTER)
        self.assertTrue(d.has(Issue.EVENT_ID_CONFLICT))

    def test_multiple_trades_in_one_tx_are_kept(self):
        # A multi-hop swap: same tx, different wallet/amount.
        v = TradeFeedValidator()
        v.process(event(event_id="a"))
        d = v.process(event(event_id="b", wallet="0xW2", amount="50"))
        self.assertIs(d.status, Status.ACCEPTED)

    def test_same_tx_different_block_time_is_conflict(self):
        v = TradeFeedValidator()
        v.process(event(event_id="a"))
        d = v.process(event(event_id="b", wallet="0xW2", block_time="10:00:12", ingested_at="10:00:15"))
        self.assertIs(d.status, Status.DEAD_LETTER)
        self.assertTrue(d.has(Issue.TX_BLOCK_TIME_CONFLICT))

    def test_evm_ids_are_case_insensitive(self):
        v = TradeFeedValidator()
        v.process(event(event_id="a", tx_hash="0xABC", wallet="0xD4aB"))
        d = v.process(event(event_id="b", tx_hash="0xabc", wallet="0xd4AB"))
        self.assertIs(d.status, Status.DUPLICATE)

    def test_non_evm_ids_keep_case(self):
        self.assertEqual(normalize_id("  7xKXtg2CW  "), "7xKXtg2CW")
        self.assertEqual(normalize_id("0xD4aB"), "0xd4ab")

    def test_dead_lettered_event_can_be_replayed_after_fix(self):
        v = TradeFeedValidator()
        self.assertIs(v.process(event(block_time=None)).status, Status.DEAD_LETTER)
        self.assertIs(v.process(event()).status, Status.ACCEPTED)


class RoundTripTest(unittest.TestCase):
    def test_buy_then_sell_same_amount_is_flagged(self):
        v = TradeFeedValidator()
        v.process(event(event_id="a", tx_hash="0x1", side="BUY"))
        d = v.process(event(event_id="b", tx_hash="0x2", side="SELL",
                            block_time="10:06:00", ingested_at="10:06:03"))
        self.assertIs(d.status, Status.ACCEPTED)
        self.assertTrue(d.has(Issue.ROUND_TRIP))

    def test_outside_window_is_not_flagged(self):
        v = TradeFeedValidator()
        v.process(event(event_id="a", tx_hash="0x1", side="BUY"))
        d = v.process(event(event_id="b", tx_hash="0x2", side="SELL",
                            block_time="12:00:00", ingested_at="12:00:03"))
        self.assertFalse(d.has(Issue.ROUND_TRIP))


if __name__ == "__main__":
    unittest.main()
