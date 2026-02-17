"""Tests for the chart_generator module."""
import json
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.chart_generator.chart_generator import (
    build_volume_distribution_chart,
    build_crypto_metrics_chart,
    build_benford_law_chart,
    build_vv_correlation_chart,
    build_buy_sell_ratio_chart,
    build_first_digit_distribution_chart,
    build_time_of_trade_chart,
    generate_all_charts,
    charts_to_shortcodes,
    replace_static_images_in_markdown,
    format_timestamp,
    _build_data_summary,
    CHART_BUILDERS,
)


# Sample market data for testing
SAMPLE_DATA = [
    {
        "timestamp": "2024-01-15T00:00:00Z",
        "volume": 1500.5,
        "tradecount": 200,
        "avgtransactionsize": 7.5,
        "buysellratio": 0.52,
        "buysellratioabs": 0.48,
        "vwap": 42500.0,
        "vvcorrelation": 0.65,
        "benfordlawtest": 0.08,
        "firstdigitdist": {"1": 60, "2": 35, "3": 25, "4": 20, "5": 15, "6": 13, "7": 11, "8": 10, "9": 9},
        "volumedist": [[i, max(0, 100 - i * 2)] for i in range(100)],
        "timeoftrade": {"seconds": [10 + (i % 5) for i in range(60)]}
    },
    {
        "timestamp": "2024-01-15T01:00:00Z",
        "volume": 1800.2,
        "tradecount": 250,
        "avgtransactionsize": 7.2,
        "buysellratio": 0.55,
        "buysellratioabs": 0.45,
        "vwap": 42600.0,
        "vvcorrelation": 0.35,
        "benfordlawtest": 0.12,
        "firstdigitdist": {"1": 70, "2": 40, "3": 28, "4": 22, "5": 18, "6": 14, "7": 12, "8": 11, "9": 10},
        "volumedist": [[i, max(0, 120 - i * 2)] for i in range(100)],
        "timeoftrade": {"seconds": [12 + (i % 3) for i in range(60)]}
    },
    {
        "timestamp": "2024-01-15T02:00:00Z",
        "volume": 900.1,
        "tradecount": 150,
        "avgtransactionsize": 6.0,
        "buysellratio": 0.38,
        "buysellratioabs": 0.62,
        "vwap": 42400.0,
        "vvcorrelation": 0.28,
        "benfordlawtest": 0.15,
        "firstdigitdist": {"1": 45, "2": 28, "3": 20, "4": 18, "5": 12, "6": 10, "7": 9, "8": 8, "9": 7},
        "volumedist": [[i, max(0, 80 - i * 2)] for i in range(100)],
        "timeoftrade": {"seconds": [8 + (i % 7) for i in range(60)]}
    }
]


def test_format_timestamp():
    result = format_timestamp("2024-01-15T00:00:00Z")
    assert "Jan" in result
    assert "15" in result
    print("  PASS: test_format_timestamp")


def test_format_timestamp_invalid():
    result = format_timestamp("not-a-date")
    assert result == "not-a-date"
    print("  PASS: test_format_timestamp_invalid")


def test_build_volume_distribution_chart():
    chart = build_volume_distribution_chart(SAMPLE_DATA)
    assert chart['id'] == 'volume-distribution'
    assert chart['config']['type'] == 'bar'
    assert len(chart['config']['data']['datasets']) == 1
    assert chart['config']['data']['datasets'][0]['data'] is not None
    assert len(chart['config']['data']['datasets'][0]['data']) > 0
    print("  PASS: test_build_volume_distribution_chart")


def test_build_crypto_metrics_chart():
    chart = build_crypto_metrics_chart(SAMPLE_DATA)
    assert chart['id'] == 'crypto-metrics'
    assert chart['config']['type'] == 'line'
    assert len(chart['config']['data']['datasets']) == 4
    assert len(chart['config']['data']['labels']) == 3
    print("  PASS: test_build_crypto_metrics_chart")


def test_build_benford_law_chart():
    chart = build_benford_law_chart(SAMPLE_DATA)
    assert chart['id'] == 'benford-law'
    assert len(chart['config']['data']['datasets']) == 2
    # Critical value should be positive for positive tradecount
    critical_values = chart['config']['data']['datasets'][1]['data']
    assert all(v > 0 for v in critical_values)
    print("  PASS: test_build_benford_law_chart")


def test_build_vv_correlation_chart():
    chart = build_vv_correlation_chart(SAMPLE_DATA)
    assert chart['id'] == 'vv-correlation'
    # Should have 2 datasets: VV correlation and threshold line
    assert len(chart['config']['data']['datasets']) == 2
    threshold_data = chart['config']['data']['datasets'][1]['data']
    assert all(v == 0.4 for v in threshold_data)
    print("  PASS: test_build_vv_correlation_chart")


def test_build_buy_sell_ratio_chart():
    chart = build_buy_sell_ratio_chart(SAMPLE_DATA)
    assert chart['id'] == 'buy-sell-ratio'
    # Should have 4 datasets: upper bound, lower bound, ratio, ratio_abs
    assert len(chart['config']['data']['datasets']) == 4
    print("  PASS: test_build_buy_sell_ratio_chart")


def test_build_first_digit_distribution_chart():
    chart = build_first_digit_distribution_chart(SAMPLE_DATA)
    assert chart['id'] == 'first-digit-distribution'
    assert chart['config']['type'] == 'bar'
    # Should have 9 labels (digits 1-9)
    assert len(chart['config']['data']['labels']) == 9
    # Should have 2 datasets: observed and expected
    assert len(chart['config']['data']['datasets']) == 2
    print("  PASS: test_build_first_digit_distribution_chart")


def test_build_time_of_trade_chart():
    chart = build_time_of_trade_chart(SAMPLE_DATA)
    assert chart['id'] == 'time-of-trade'
    # Should have 60 labels (seconds 0-59)
    assert len(chart['config']['data']['labels']) == 60
    print("  PASS: test_build_time_of_trade_chart")


def test_generate_all_charts():
    charts = generate_all_charts(SAMPLE_DATA)
    assert len(charts) == len(CHART_BUILDERS)
    chart_ids = {c['id'] for c in charts}
    expected_ids = {
        'volume-distribution', 'crypto-metrics', 'benford-law',
        'vv-correlation', 'buy-sell-ratio', 'first-digit-distribution',
        'time-of-trade'
    }
    assert chart_ids == expected_ids
    print("  PASS: test_generate_all_charts")


def test_charts_to_shortcodes():
    charts = generate_all_charts(SAMPLE_DATA)
    shortcodes = charts_to_shortcodes(charts)
    assert len(shortcodes) == len(charts)
    for sc in shortcodes:
        assert '{{< dynamic_chart' in sc
        assert '{{< /dynamic_chart >}}' in sc
    print("  PASS: test_charts_to_shortcodes")


def test_chart_config_is_valid_json():
    charts = generate_all_charts(SAMPLE_DATA)
    for chart in charts:
        config_json = json.dumps(chart['config'])
        parsed = json.loads(config_json)
        assert isinstance(parsed, dict)
    print("  PASS: test_chart_config_is_valid_json")


def test_replace_static_images():
    charts = generate_all_charts(SAMPLE_DATA)
    md = '{{< figure src="volume_hist.png" alt="test" caption="Volume distribution" loading="lazy" >}}'
    result = replace_static_images_in_markdown(md, charts)
    assert 'volume_hist.png' not in result
    assert 'dynamic_chart' in result
    print("  PASS: test_replace_static_images")


def test_build_data_summary():
    summary = _build_data_summary(SAMPLE_DATA)
    assert summary['record_count'] == 3
    assert 'volume' in summary['metrics']
    assert 'vvcorrelation' in summary['metrics']
    assert summary['vv_below_threshold'] == 2  # 0.35 and 0.28 are below 0.4
    assert summary['bsr_abnormal_count'] == 1  # 0.38 is below 0.4
    print("  PASS: test_build_data_summary")


def test_empty_data():
    charts = generate_all_charts([])
    # Should not crash, may produce charts with empty data
    assert isinstance(charts, list)
    print("  PASS: test_empty_data")


if __name__ == '__main__':
    print("Running chart_generator tests...")
    test_format_timestamp()
    test_format_timestamp_invalid()
    test_build_volume_distribution_chart()
    test_build_crypto_metrics_chart()
    test_build_benford_law_chart()
    test_build_vv_correlation_chart()
    test_build_buy_sell_ratio_chart()
    test_build_first_digit_distribution_chart()
    test_build_time_of_trade_chart()
    test_generate_all_charts()
    test_charts_to_shortcodes()
    test_chart_config_is_valid_json()
    test_replace_static_images()
    test_build_data_summary()
    test_empty_data()
    print("\nAll tests passed!")
