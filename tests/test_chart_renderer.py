"""
🌰 Tests for ChartRenderer — validates Chart.js JSON generation from market data.
"""
import json
import os
import tempfile
import pytest
import pandas as pd
import numpy as np

from tools.python_modules.chart_renderer import ChartRenderer


@pytest.fixture
def sample_data():
    """Generate sample market health data similar to API response."""
    np.random.seed(42)
    n = 48  # 48 hours of data
    timestamps = pd.date_range("2024-01-01", periods=n, freq="h")
    return [
        {
            "timestamp": ts.isoformat(),
            "volume": float(np.random.exponential(1000)),
            "tradecount": int(np.random.randint(50, 500)),
            "avgtransactionsize": float(np.random.uniform(0.1, 10)),
            "buysellratio": float(np.random.uniform(0.3, 0.7)),
            "benfordlawtest": float(np.random.uniform(0.01, 0.15)),
            "vvcorrelation": float(np.random.uniform(0.1, 0.9)),
        }
        for ts in timestamps
    ]


@pytest.fixture
def renderer():
    return ChartRenderer()


@pytest.fixture
def output_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestChartRenderer:
    def test_generate_report_creates_all_files(self, renderer, sample_data, output_dir):
        """🌰 All four JSON chart files should be created."""
        filenames = renderer.generate_report(sample_data, output_dir)
        assert len(filenames) == 4
        expected = ["volume_hist.json", "crypto_metrics.json", "benford_law.json", "vv_correlation.json"]
        for name in expected:
            assert name in filenames
            assert os.path.exists(os.path.join(output_dir, name))

    def test_volume_hist_valid_chartjs(self, renderer, sample_data, output_dir):
        """🌰 Volume histogram should be valid Chart.js bar config."""
        df = pd.DataFrame(sample_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        renderer.make_volume_hist(df, output_dir)

        with open(os.path.join(output_dir, "volume_hist.json")) as f:
            config = json.load(f)
        assert config["type"] == "bar"
        assert len(config["data"]["labels"]) == 30
        assert len(config["data"]["datasets"]) == 1
        assert config["data"]["datasets"][0]["label"] == "Frequency"

    def test_crypto_metrics_has_four_datasets(self, renderer, sample_data, output_dir):
        """🌰 Crypto metrics chart should have 4 datasets."""
        df = pd.DataFrame(sample_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        renderer.make_crypto_metrics(df, output_dir)

        with open(os.path.join(output_dir, "crypto_metrics.json")) as f:
            config = json.load(f)
        assert config["type"] == "line"
        assert len(config["data"]["datasets"]) == 4
        labels = [ds["label"] for ds in config["data"]["datasets"]]
        assert "Volume" in labels
        assert "Trade Count" in labels
        assert "Buy/Sell Ratio" in labels

    def test_benford_law_dual_axis(self, renderer, sample_data, output_dir):
        """🌰 Benford law chart should have dual y-axes."""
        df = pd.DataFrame(sample_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        renderer.make_benford_law(df, output_dir)

        with open(os.path.join(output_dir, "benford_law.json")) as f:
            config = json.load(f)
        assert "y-test" in config["options"]["scales"]
        assert "y-critical" in config["options"]["scales"]
        assert len(config["data"]["datasets"]) == 2

    def test_vv_correlation_has_threshold(self, renderer, sample_data, output_dir):
        """🌰 VV correlation chart should include 0.4 threshold line."""
        df = pd.DataFrame(sample_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        renderer.make_vv_correlation(df, output_dir)

        with open(os.path.join(output_dir, "vv_correlation.json")) as f:
            config = json.load(f)
        datasets = config["data"]["datasets"]
        threshold_ds = [ds for ds in datasets if "Threshold" in ds["label"]]
        assert len(threshold_ds) == 1
        assert all(v == 0.4 for v in threshold_ds[0]["data"])

    def test_json_files_are_valid(self, renderer, sample_data, output_dir):
        """🌰 All generated files should be valid JSON."""
        renderer.generate_report(sample_data, output_dir)
        for fname in os.listdir(output_dir):
            if fname.endswith(".json"):
                with open(os.path.join(output_dir, fname)) as f:
                    data = json.load(f)
                assert "type" in data
                assert "data" in data
                assert "options" in data

    def test_creates_directory_if_missing(self, renderer, sample_data, output_dir):
        """🌰 Should create output directory if it doesn't exist."""
        new_dir = os.path.join(output_dir, "subdir", "charts")
        renderer.generate_report(sample_data, new_dir)
        assert os.path.isdir(new_dir)
        assert len(os.listdir(new_dir)) == 4
