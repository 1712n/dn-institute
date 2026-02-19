"""
🌰 Chart Renderer — generates Chart.js JSON configurations from market health data.
Replaces matplotlib PNG generation with dynamic, interactive charts.
"""
import json
import os
import numpy as np
import pandas as pd


class ChartRenderer:
    """Generates Chart.js JSON config files from market health data."""

    # 🌰 Color palette for charts
    COLORS = {
        'blue': 'rgba(54, 162, 235, {a})',
        'red': 'rgba(255, 99, 132, {a})',
        'green': 'rgba(75, 192, 192, {a})',
        'orange': 'rgba(255, 159, 64, {a})',
        'purple': 'rgba(153, 102, 255, {a})',
        'grey': 'rgba(201, 203, 207, {a})',
    }

    def __init__(self):
        pass

    @staticmethod
    def _color(name, alpha=1.0):
        return ChartRenderer.COLORS.get(name, 'rgba(0,0,0,{a})').format(a=alpha)

    @staticmethod
    def _save(config, directory, filename):
        path = os.path.join(directory, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
        return filename

    def make_volume_hist(self, data, directory):
        """🌰 Volume distribution histogram."""
        volumes = data['volume'].dropna().tolist()
        counts, bin_edges = np.histogram(volumes, bins=30)
        labels = [
            f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}"
            for i in range(len(counts))
        ]
        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Frequency",
                    "data": counts.tolist(),
                    "backgroundColor": self._color('blue', 0.6),
                    "borderColor": self._color('blue', 1.0),
                    "borderWidth": 1
                }]
            },
            "options": {
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Transaction Volume Distribution"
                    }
                },
                "scales": {
                    "x": {"title": {"display": True, "text": "Transaction Volume"}},
                    "y": {"title": {"display": True, "text": "Frequency"}}
                }
            }
        }
        return self._save(config, directory, "volume_hist.json")

    def make_crypto_metrics(self, data, directory):
        """🌰 Multi-line crypto metrics: volume, trade count, avg tx size, buy/sell ratio."""
        timestamps = data.index.strftime('%Y-%m-%d %H:%M').tolist()
        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Volume",
                        "data": data['volume'].tolist(),
                        "borderColor": self._color('blue', 1.0),
                        "backgroundColor": self._color('blue', 0.1),
                        "yAxisID": "y-volume",
                        "fill": False,
                        "tension": 0.3,
                        "pointRadius": 0
                    },
                    {
                        "label": "Trade Count",
                        "data": data['tradecount'].tolist(),
                        "borderColor": self._color('green', 1.0),
                        "backgroundColor": self._color('green', 0.1),
                        "yAxisID": "y-tradecount",
                        "fill": False,
                        "tension": 0.3,
                        "pointRadius": 0
                    },
                    {
                        "label": "Avg Transaction Size",
                        "data": data['avgtransactionsize'].tolist(),
                        "borderColor": self._color('orange', 1.0),
                        "backgroundColor": self._color('orange', 0.1),
                        "yAxisID": "y-avgsize",
                        "fill": False,
                        "tension": 0.3,
                        "pointRadius": 0
                    },
                    {
                        "label": "Buy/Sell Ratio",
                        "data": data['buysellratio'].tolist(),
                        "borderColor": self._color('red', 1.0),
                        "backgroundColor": self._color('red', 0.1),
                        "yAxisID": "y-buysell",
                        "fill": False,
                        "tension": 0.3,
                        "pointRadius": 0
                    }
                ]
            },
            "options": {
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {"display": True, "text": "Cryptocurrency Metrics Over Time"},
                    "tooltip": {"mode": "index", "intersect": False}
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Timestamp"},
                        "ticks": {"maxTicksLimit": 20, "maxRotation": 45}
                    },
                    "y-volume": {
                        "type": "linear", "position": "left", "display": True,
                        "title": {"display": True, "text": "Volume"},
                        "grid": {"drawOnChartArea": True}
                    },
                    "y-tradecount": {
                        "type": "linear", "position": "right", "display": False
                    },
                    "y-avgsize": {
                        "type": "linear", "position": "right", "display": False
                    },
                    "y-buysell": {
                        "type": "linear", "position": "right", "display": False
                    }
                }
            }
        }
        return self._save(config, directory, "crypto_metrics.json")

    def make_benford_law(self, data, directory):
        """🌰 Benford's Law test score with K-S critical value threshold line."""
        timestamps = data.index.strftime('%Y-%m-%d %H:%M').tolist()
        ks_critical = (1.36 / np.sqrt(data['tradecount'])).tolist()
        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Benford Law Test Score",
                        "data": data['benfordlawtest'].tolist(),
                        "borderColor": self._color('blue', 1.0),
                        "backgroundColor": self._color('blue', 0.1),
                        "yAxisID": "y-test",
                        "fill": False,
                        "tension": 0.3,
                        "pointRadius": 1
                    },
                    {
                        "label": "K-S Critical Value (1.36/\u221an)",
                        "data": ks_critical,
                        "borderColor": self._color('green', 1.0),
                        "backgroundColor": self._color('green', 0.1),
                        "yAxisID": "y-critical",
                        "fill": False,
                        "borderDash": [5, 5],
                        "tension": 0.3,
                        "pointRadius": 0
                    }
                ]
            },
            "options": {
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {"display": True, "text": "Benford Law Test Score and Critical Value Over Time"},
                    "tooltip": {"mode": "index", "intersect": False}
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Timestamp"},
                        "ticks": {"maxTicksLimit": 20, "maxRotation": 45}
                    },
                    "y-test": {
                        "type": "linear", "position": "left",
                        "title": {"display": True, "text": "Benford Law Test Score"}
                    },
                    "y-critical": {
                        "type": "linear", "position": "right",
                        "title": {"display": True, "text": "K-S Critical Value"},
                        "grid": {"drawOnChartArea": False}
                    }
                }
            }
        }
        return self._save(config, directory, "benford_law.json")

    def make_vv_correlation(self, data, directory):
        """🌰 Volume-Volatility correlation with 0.4 suspicion threshold."""
        timestamps = data.index.strftime('%Y-%m-%d %H:%M').tolist()
        threshold_data = [0.4] * len(timestamps)
        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "VV Correlation",
                        "data": data['vvcorrelation'].tolist(),
                        "borderColor": self._color('purple', 1.0),
                        "backgroundColor": self._color('purple', 0.1),
                        "fill": False,
                        "tension": 0.3,
                        "pointRadius": 2,
                        "pointBackgroundColor": self._color('purple', 1.0)
                    },
                    {
                        "label": "Suspicion Threshold (0.4)",
                        "data": threshold_data,
                        "borderColor": self._color('red', 0.7),
                        "borderDash": [10, 5],
                        "fill": False,
                        "pointRadius": 0,
                        "borderWidth": 2
                    }
                ]
            },
            "options": {
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {"display": True, "text": "Volume-Volatility Correlation Over Time"},
                    "tooltip": {"mode": "index", "intersect": False}
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Timestamp"},
                        "ticks": {"maxTicksLimit": 20, "maxRotation": 45}
                    },
                    "y": {
                        "title": {"display": True, "text": "VV Correlation"},
                        "suggestedMin": 0,
                        "suggestedMax": 1
                    }
                }
            }
        }
        return self._save(config, directory, "vv_correlation.json")

    def generate_report(self, data, directory):
        """🌰 Generate all chart JSON files from market data."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        data = pd.DataFrame(data)
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.set_index('timestamp', inplace=True)

        filenames = []
        filenames.append(self.make_volume_hist(data, directory))
        filenames.append(self.make_crypto_metrics(data, directory))
        filenames.append(self.make_benford_law(data, directory))
        filenames.append(self.make_vv_correlation(data, directory))
        return filenames
