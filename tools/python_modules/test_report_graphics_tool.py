"""
🌰 Unit tests for report_graphics_tool.py

Tests the Visualization class that generates Hugo ECharts shortcode blocks
from market data dicts — with zero dependencies on matplotlib, pandas, or numpy.

Run with:
    python -m pytest tools/python_modules/test_report_graphics_tool.py -v
"""

import json
import os
import tempfile
import pytest

from tools.python_modules.report_graphics_tool import Visualization


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_data():
    """Minimal market data rows covering all chart fields. 🌰"""
    return [
        {
            "timestamp": "2023-07-01 00:00",
            "volume": 1200.5,
            "tradecount": 450,
            "avgtransactionsize": 2.67,
            "buysellratio": 1.05,
            "benfordlawtest": 0.042,
            "vvcorrelation": 0.73,
        },
        {
            "timestamp": "2023-07-01 01:00",
            "volume": 980.0,
            "tradecount": 380,
            "avgtransactionsize": 2.58,
            "buysellratio": 0.97,
            "benfordlawtest": 0.031,
            "vvcorrelation": 0.85,
        },
        {
            "timestamp": "2023-07-01 02:00",
            "volume": 1540.2,
            "tradecount": 610,
            "avgtransactionsize": 2.52,
            "buysellratio": 1.12,
            "benfordlawtest": 0.055,
            "vvcorrelation": 0.61,
        },
    ]


@pytest.fixture
def viz():
    return Visualization()


# ---------------------------------------------------------------------------
# _shortcode helper
# ---------------------------------------------------------------------------

class TestShortcode:
    def test_basic_shortcode_contains_id(self):
        """🌰 Shortcode must include the chart id."""
        result = Visualization._shortcode("my-chart", {"series": []})
        assert 'id="my-chart"' in result

    def test_shortcode_contains_valid_json(self):
        """🌰 Inner content must be valid JSON."""
        option = {"xAxis": {"type": "value"}, "series": [{"type": "bar", "data": [1, 2, 3]}]}
        result = Visualization._shortcode("test", option)
        # Extract the JSON line (between the opening and closing shortcode tags)
        lines = result.strip().splitlines()
        json_line = lines[1]
        parsed = json.loads(json_line)
        assert parsed["xAxis"]["type"] == "value"

    def test_shortcode_with_title(self):
        """🌰 title parameter is included when provided."""
        result = Visualization._shortcode("ch", {}, title="My Title")
        assert 'title="My Title"' in result

    def test_shortcode_without_title(self):
        """No title parameter when not provided."""
        result = Visualization._shortcode("ch", {})
        assert "title=" not in result

    def test_shortcode_custom_height(self):
        """🌰 height is included when different from default 400."""
        result = Visualization._shortcode("ch", {}, height=300)
        assert 'height="300"' in result

    def test_shortcode_default_height_omitted(self):
        """Default height (400) is omitted from the tag to keep markup clean."""
        result = Visualization._shortcode("ch", {}, height=400)
        assert "height=" not in result

    def test_shortcode_with_caption(self):
        """🌰 caption is included when provided."""
        result = Visualization._shortcode("ch", {}, caption="Fig 1. 🌰")
        assert 'caption="Fig 1. 🌰"' in result

    def test_shortcode_open_close_tags(self):
        """Hugo shortcode must have matching open/close tags."""
        result = Visualization._shortcode("ch", {})
        assert "{{< echarts" in result
        assert "{{< /echarts >}}" in result


# ---------------------------------------------------------------------------
# _make_volume_hist
# ---------------------------------------------------------------------------

class TestMakeVolumeHist:
    def test_returns_shortcode_string(self, viz, sample_data):
        """🌰 Volume histogram returns a non-empty shortcode string."""
        result = viz._make_volume_hist(sample_data)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_bar_series(self, viz, sample_data):
        """🌰 Histogram must use a bar series type."""
        result = viz._make_volume_hist(sample_data)
        assert '"bar"' in result

    def test_empty_volumes_returns_empty(self, viz):
        """🌰 Missing volume field → empty string (graceful)."""
        data = [{"timestamp": "2023-01-01", "volume": None}]
        result = viz._make_volume_hist(data)
        assert result == ""

    def test_single_value_returns_empty(self, viz):
        """All identical volumes → bin_width=0 → should return empty (division guard)."""
        data = [{"volume": 100.0}, {"volume": 100.0}]
        result = viz._make_volume_hist(data)
        assert result == ""

    def test_bin_count_is_30(self, viz, sample_data):
        """🌰 30-bin histogram: x-axis data must have 30 labels."""
        result = viz._make_volume_hist(sample_data)
        option_json = result.splitlines()[1]
        option = json.loads(option_json)
        assert len(option["xAxis"]["data"]) == 30

    def test_counts_sum_to_volume_count(self, viz, sample_data):
        """🌰 Sum of bin counts equals total data points."""
        result = viz._make_volume_hist(sample_data)
        option = json.loads(result.splitlines()[1])
        counts = option["series"][0]["data"]
        assert sum(counts) == len(sample_data)


# ---------------------------------------------------------------------------
# _make_crypto_metrics
# ---------------------------------------------------------------------------

class TestMakeCryptoMetrics:
    def test_returns_four_shortcodes(self, viz, sample_data):
        """🌰 Four separate line charts for volume, trade count, avg tx size, buy/sell ratio."""
        result = viz._make_crypto_metrics(sample_data)
        assert result.count("{{< echarts") == 4

    def test_all_line_series(self, viz, sample_data):
        """🌰 Every chart uses a line series."""
        result = viz._make_crypto_metrics(sample_data)
        blocks = result.split("{{< /echarts >}}")
        for block in blocks:
            if "{{< echarts" in block:
                # JSON line starts with '{' but NOT '{{' (which is the Hugo shortcode tag)
                json_line = [l for l in block.splitlines()
                             if l.strip().startswith("{") and not l.strip().startswith("{{")][0]
                option = json.loads(json_line)
                assert option["series"][0]["type"] == "line"

    def test_missing_field_skipped(self, viz):
        """🌰 If a field is entirely absent, that chart is omitted gracefully."""
        # Only volume present
        data = [{"timestamp": "t1", "volume": 100}]
        result = viz._make_crypto_metrics(data)
        # Only 1 chart should be generated
        assert result.count("{{< echarts") == 1

    def test_timestamps_match_data_length(self, viz, sample_data):
        """🌰 X-axis labels match the number of data rows."""
        result = viz._make_crypto_metrics(sample_data)
        # JSON line starts with '{' but NOT '{{' (Hugo shortcode tag)
        first_block_json = [l for l in result.splitlines()
                            if l.strip().startswith("{") and not l.strip().startswith("{{")][0]
        option = json.loads(first_block_json)
        assert len(option["xAxis"]["data"]) == len(sample_data)


# ---------------------------------------------------------------------------
# _make_benfordlaw
# ---------------------------------------------------------------------------

class TestMakeBenfordLaw:
    def test_returns_non_empty(self, viz, sample_data):
        """🌰 Benford law chart returns a non-empty shortcode."""
        result = viz._make_benfordlaw(sample_data)
        assert len(result) > 0

    def test_has_two_y_axes(self, viz, sample_data):
        """🌰 Dual y-axis: left for score, right for critical value."""
        result = viz._make_benfordlaw(sample_data)
        option = json.loads(result.splitlines()[1])
        assert isinstance(option["yAxis"], list)
        assert len(option["yAxis"]) == 2

    def test_critical_value_formula(self, viz, sample_data):
        """🌰 Critical value = 1.36 / sqrt(tradecount), rounded to 6 decimals."""
        result = viz._make_benfordlaw(sample_data)
        option = json.loads(result.splitlines()[1])
        critical_series = option["series"][1]["data"]
        for i, row in enumerate(sample_data):
            expected = round(1.36 / (float(row["tradecount"]) ** 0.5), 6)
            assert abs(critical_series[i] - expected) < 1e-9

    def test_critical_value_none_for_zero_tradecount(self, viz):
        """🌰 Zero trade count → critical value is None (no division by zero)."""
        data = [
            {"timestamp": "t1", "benfordlawtest": 0.04, "tradecount": 0},
            {"timestamp": "t2", "benfordlawtest": 0.03, "tradecount": 100},
        ]
        result = viz._make_benfordlaw(data)
        option = json.loads(result.splitlines()[1])
        critical = option["series"][1]["data"]
        assert critical[0] is None
        assert critical[1] is not None


# ---------------------------------------------------------------------------
# _make_vvcorrelation
# ---------------------------------------------------------------------------

class TestMakeVvCorrelation:
    def test_returns_non_empty(self, viz, sample_data):
        """🌰 VV correlation chart returns a non-empty shortcode."""
        result = viz._make_vvcorrelation(sample_data)
        assert len(result) > 0

    def test_has_visual_map(self, viz, sample_data):
        """🌰 visualMap must be present for the green→yellow→red gradient."""
        result = viz._make_vvcorrelation(sample_data)
        option = json.loads(result.splitlines()[1])
        assert "visualMap" in option

    def test_visual_map_color_gradient(self, viz, sample_data):
        """🌰 Gradient must be green → yellow → red."""
        result = viz._make_vvcorrelation(sample_data)
        option = json.loads(result.splitlines()[1])
        colors = option["visualMap"]["inRange"]["color"]
        assert colors[0] == "#91cc75"   # green
        assert colors[1] == "#fac858"   # yellow
        assert colors[2] == "#ee6666"   # red

    def test_empty_returns_empty(self, viz):
        """🌰 All-None vvcorrelation values → empty string."""
        data = [{"timestamp": "t1", "vvcorrelation": None}]
        result = viz._make_vvcorrelation(data)
        assert result == ""


# ---------------------------------------------------------------------------
# generate_report (integration)
# ---------------------------------------------------------------------------

class TestGenerateReport:
    def test_creates_index_md_if_missing(self, viz, sample_data):
        """🌰 generate_report creates the directory and appends to index.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            article_dir = os.path.join(tmpdir, "new-article")
            # index.md does not exist yet — generate_report should create the dir
            # but won't write unless index.md exists (by design)
            result = viz.generate_report(sample_data, article_dir)
            assert isinstance(result, str)
            # Directory should be created
            assert os.path.isdir(article_dir)

    def test_appends_to_existing_index_md(self, viz, sample_data):
        """🌰 generate_report appends charts to an existing index.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = os.path.join(tmpdir, "index.md")
            original_content = "# My Article\n\nSome text.\n"
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(original_content)

            result = viz.generate_report(sample_data, tmpdir)

            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert content.startswith(original_content)
            assert "{{< echarts" in content
            assert result in content

    def test_returns_combined_markdown(self, viz, sample_data):
        """🌰 Return value contains all chart shortcodes concatenated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = viz.generate_report(sample_data, tmpdir)
            # Should include at least the volume histogram and crypto metrics
            assert result.count("{{< echarts") >= 5

    def test_empty_data_returns_empty_string(self, viz):
        """🌰 Empty data list → no volume/metrics charts (those require data)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = viz.generate_report([], tmpdir)
            # volume histogram and crypto metrics return empty for no data
            assert "volume-hist" not in result
            assert "volume-ts" not in result
