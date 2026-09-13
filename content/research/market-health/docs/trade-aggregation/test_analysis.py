import unittest
from decimal import Decimal

import analysis


def trade(identifier, quantity="1", timestamp=100, price="2", maker=True, best=True):
    return analysis.Trade(identifier, Decimal(price), Decimal(quantity), Decimal(quantity) * Decimal(price), timestamp, maker, best)


def aggregate(identifier, first, last, quantity="2", timestamp=101, price="2", maker=True, best=True):
    return analysis.AggregateTrade(identifier, Decimal(price), Decimal(quantity), first, last, timestamp, maker, best)


class ReconciliationTests(unittest.TestCase):
    def test_exact_range_quantity_price_flags_and_time_pass(self):
        raw = [trade(10, "1", 100), trade(11, "1", 101)]
        result = analysis.reconciliation(raw, [aggregate(1, 10, 11)])
        self.assertTrue(result["all_checks_passed"])
        self.assertEqual(result["aggregate_timestamps_equal_last_raw_timestamp_count"], 1)
        self.assertTrue(result["total_base_quantity"]["matches_exactly"])
        self.assertEqual(result["total_base_quantity"]["raw_trades"], "2")

    def test_reconciliation_reports_exact_quantity_mismatch(self):
        raw = [trade(10, "1", 100), trade(11, "1", 101)]
        result = analysis.reconciliation(raw, [aggregate(1, 10, 11, quantity="1.9")])
        self.assertEqual(result["failure_counts"]["quantity_mismatch"], 1)
        self.assertFalse(result["all_checks_passed"])

    def test_reconciliation_reports_noncontiguous_range_and_time_escape(self):
        raw = [trade(10, "1", 100), trade(12, "1", 101)]
        result = analysis.reconciliation(raw, [aggregate(1, 10, 12, timestamp=200)])
        self.assertEqual(result["failure_counts"]["missing_or_noncontiguous_id_range"], 1)
        self.assertEqual(result["failure_counts"]["timestamp_outside_raw_range"], 1)

    def test_metrics_raises_data_error_for_missing_aggregate_endpoint(self):
        raw = [trade(10, "1", 100)]
        malformed = [aggregate(1, 10, 11, quantity="1", timestamp=100)]
        with self.assertRaisesRegex(analysis.DataError, "aggregate reconciliation failed"):
            analysis.metrics(raw, malformed)

    def test_metrics_preserves_valid_sample_output(self):
        raw = [trade(10, "1", 100), trade(11, "1", 101)]
        result = analysis.metrics(raw, [aggregate(1, 10, 11)])
        self.assertTrue(result["reconciliation"]["all_checks_passed"])
        self.assertEqual(result["sample_counts"], {
            "raw_trades": 2,
            "aggregate_trades": 1,
            "raw_trades_per_aggregate_trade": "2",
        })

    def test_first_digit_and_round_rate_use_decimal_not_float(self):
        quantities = [Decimal("0.00100"), Decimal("10.000"), Decimal("2.5")]
        self.assertEqual(analysis.first_digit(quantities[0]), "1")
        rate = analysis.round_rate(quantities)
        self.assertEqual(rate["count"], 1)
        self.assertEqual(rate["rate"], "0.33333333333333333333333333333333333333333333333333")

    def test_benford_diagnostics_and_total_variation_are_decimal_descriptive_metrics(self):
        left = analysis.distribution([Decimal("1"), Decimal("2")])
        right = analysis.distribution([Decimal("1"), Decimal("1")])
        diagnostics = analysis.benford_diagnostics(left)
        self.assertEqual(diagnostics["benford_expected_rates"]["1"], format(analysis.benford_probability(1), "f"))
        self.assertGreater(Decimal(diagnostics["mean_absolute_deviation"]), 0)
        self.assertEqual(analysis.total_variation_distance(left, right), "0.5")

    def test_hourly_rates_exclude_cross_hour_aggregate_ranges(self):
        raw = [
            trade(10, "2", analysis.DAY_START_US + 3_599_999_999),
            trade(11, "2", analysis.DAY_START_US + 3_600_000_000),
        ]
        aggregates = [aggregate(1, 10, 11, timestamp=analysis.DAY_START_US + 3_600_000_000)]
        result = analysis.hourly_leading_digit_two(raw, aggregates)
        self.assertEqual(result["aggregate_ranges_crossing_utc_hour_boundary"], 1)
        self.assertEqual(result["hours_utc"]["00"]["aggregate_trades"]["row_count"], 0)
        self.assertEqual(result["hours_utc"]["01"]["aggregate_trades"]["row_count"], 0)

    def test_timestamp_info_marks_outside_requested_day(self):
        raw = [trade(10, "1", analysis.DAY_END_US)]
        aggregates = [aggregate(1, 10, 10, quantity="1", timestamp=analysis.DAY_END_US)]
        self.assertFalse(analysis.timestamp_info(raw, aggregates)["all_timestamps_within_requested_utc_day"])


if __name__ == "__main__":
    unittest.main()
