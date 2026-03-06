"""
🌰 Tests for the interactive Chart.js report graphics tool 🌰

Validates that the Visualization class generates correct Hugo shortcodes
with properly formatted Chart.js data instead of static matplotlib PNGs.
"""

import json
import os
import tempfile
import pytest
from report_graphics_tool import Visualization


# 🌰 Sample market health data matching the API response format
SAMPLE_DATA = [
    {
        "timestamp": "2023-07-01T00:00:00",
        "volume": 1500.5,
        "tradecount": 200,
        "avgtransactionsize": 7.5,
        "buysellratio": 0.52,
        "benfordlawtest": 0.08,
        "vvcorrelation": 0.35,
        "vwap": 30100.0,
        "buysellratioabs": 0.48
    },
    {
        "timestamp": "2023-07-01T01:00:00",
        "volume": 2300.1,
        "tradecount": 310,
        "avgtransactionsize": 7.4,
        "buysellratio": 0.55,
        "benfordlawtest": 0.12,
        "vvcorrelation": 0.42,
        "vwap": 30150.0,
        "buysellratioabs": 0.45
    },
    {
        "timestamp": "2023-07-01T02:00:00",
        "volume": 800.0,
        "tradecount": 150,
        "avgtransactionsize": 5.3,
        "buysellratio": 0.48,
        "benfordlawtest": 0.15,
        "vvcorrelation": 0.28,
        "vwap": 30050.0,
        "buysellratioabs": 0.52
    },
    {
        "timestamp": "2023-07-01T03:00:00",
        "volume": 3200.7,
        "tradecount": 450,
        "avgtransactionsize": 7.1,
        "buysellratio": 0.61,
        "benfordlawtest": 0.06,
        "vvcorrelation": 0.55,
        "vwap": 30200.0,
        "buysellratioabs": 0.39
    },
    {
        "timestamp": "2023-07-01T04:00:00",
        "volume": 1100.3,
        "tradecount": 180,
        "avgtransactionsize": 6.1,
        "buysellratio": 0.50,
        "benfordlawtest": 0.10,
        "vvcorrelation": 0.38,
        "vwap": 30120.0,
        "buysellratioabs": 0.50
    }
]


class TestVisualization:
    """🌰 Test suite for the interactive chart generation 🌰"""

    def setup_method(self):
        self.vis = Visualization()
        self.tmpdir = tempfile.mkdtemp()

    def test_generate_report_returns_dict(self):
        """🌰 generate_report should return a dict of chart shortcodes"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        assert isinstance(result, dict)
        assert len(result) == 4

    def test_generate_report_has_all_charts(self):
        """🌰 All four chart types should be present"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        expected_keys = ['volume_hist', 'crypto_metrics', 'benford_law', 'vv_correlation']
        for key in expected_keys:
            assert key in result, f"Missing chart: {key}"

    def test_shortcodes_contain_metric_chart(self):
        """🌰 Each shortcode should use the metric_chart Hugo shortcode"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        for name, shortcode in result.items():
            assert '{{< metric_chart' in shortcode, f"{name} missing metric_chart shortcode"
            assert '>}}' in shortcode, f"{name} missing closing shortcode tag"

    def test_shortcodes_have_valid_json_data(self):
        """🌰 Chart data attributes should contain valid JSON"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        for name, shortcode in result.items():
            # Extract the data attribute value
            data_start = shortcode.index("data='") + len("data='")
            data_end = shortcode.index("'", data_start)
            data_json = shortcode[data_start:data_end]
            parsed = json.loads(data_json)
            assert 'labels' in parsed, f"{name} data missing labels"
            assert 'datasets' in parsed, f"{name} data missing datasets"

    def test_shortcodes_have_unique_ids(self):
        """🌰 Each chart should have a unique ID"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        ids = set()
        for shortcode in result.values():
            id_start = shortcode.index('id="') + len('id="')
            id_end = shortcode.index('"', id_start)
            chart_id = shortcode[id_start:id_end]
            assert chart_id not in ids, f"Duplicate chart ID: {chart_id}"
            ids.add(chart_id)

    def test_fragment_file_created(self):
        """🌰 A chart_shortcodes.md fragment file should be created"""
        self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        fragment_path = os.path.join(self.tmpdir, 'chart_shortcodes.md')
        assert os.path.exists(fragment_path)
        with open(fragment_path, 'r') as f:
            content = f.read()
        assert 'metric_chart' in content

    def test_volume_hist_has_bar_type(self):
        """🌰 Volume histogram should be a bar chart"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        assert 'type="bar"' in result['volume_hist']

    def test_crypto_metrics_has_line_type(self):
        """🌰 Crypto metrics should be a line chart"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        assert 'type="line"' in result['crypto_metrics']

    def test_benford_law_has_dual_axes(self):
        """🌰 Benford law chart should have dual Y-axes"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        shortcode = result['benford_law']
        options_start = shortcode.index("options='") + len("options='")
        options_end = shortcode.index("'", options_start)
        options = json.loads(shortcode[options_start:options_end])
        assert 'y' in options['scales']
        assert 'y2' in options['scales']

    def test_vv_correlation_has_threshold(self):
        """🌰 VV correlation chart should include the 0.4 anomaly threshold line"""
        result = self.vis.generate_report(SAMPLE_DATA, self.tmpdir)
        shortcode = result['vv_correlation']
        assert 'Anomaly Threshold' in shortcode

    def test_output_directory_created(self):
        """🌰 Output directory should be created if it doesn't exist"""
        new_dir = os.path.join(self.tmpdir, 'nested', 'output')
        self.vis.generate_report(SAMPLE_DATA, new_dir)
        assert os.path.isdir(new_dir)

    def test_no_matplotlib_import(self):
        """🌰 The module should not import matplotlib"""
        import report_graphics_tool
        source_file = report_graphics_tool.__file__
        with open(source_file, 'r') as f:
            source = f.read()
        assert 'import matplotlib' not in source, "matplotlib should not be imported"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
