"""
Report Graphics Tool — Generates Chart.js JSON configurations for market health reports.

Replaces matplotlib PNG generation with dynamic, client-side Chart.js rendering.
Charts are rendered via the {{< dynamic_chart >}} Hugo shortcode.

🌰 Key design decisions:
  - Output native Chart.js config (no custom schema — direct pass-through to Chart constructor)
  - Keep backward compatibility: generate_report() returns list of generated filenames
  - JSON files sit alongside the article index.md in the same Hugo page bundle
"""

import json
import os
import pandas as pd
import numpy as np


class Visualization:
    """Generates Chart.js configuration JSON files for market health report charts."""

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _save_json(config: dict, directory: str, filename: str) -> str:
        """Serialize a Chart.js config dict to JSON and return the filename."""
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
        return filename

    @staticmethod
    def _iso_timestamps(data: pd.DataFrame) -> list:
        """Convert DataFrame index to ISO-format strings for Chart.js labels."""
        return [ts.isoformat() for ts in data.index]

    # ------------------------------------------------------------------
    # Individual chart builders (each returns a Chart.js config dict)
    # ------------------------------------------------------------------

    def _make_volume_hist(self, data: pd.DataFrame, directory: str) -> str:
        """Transaction volume histogram — bar chart.  🌰"""
        volumes = data['volume'].dropna()
        hist_values, bin_edges = np.histogram(volumes, bins=30)
        labels = [
            f"{bin_edges[i]:.2f}–{bin_edges[i+1]:.2f}"
            for i in range(len(hist_values))
        ]

        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Frequency",
                    "data": hist_values.tolist(),
                    "backgroundColor": "rgba(135,206,235,0.7)",
                    "borderColor": "rgba(0,0,0,0.8)",
                    "borderWidth": 1,
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Transaction Volume Distribution"},
                    "legend": {"display": False},
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Transaction Volume"},
                        "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 15},
                    },
                    "y": {
                        "title": {"display": True, "text": "Frequency"},
                        "beginAtZero": True,
                    },
                },
            },
        }
        return self._save_json(config, directory, 'volume_hist.json')

    def _make_crypto_metrics(self, data: pd.DataFrame, directory: str) -> str:
        """4-panel crypto metrics (volume, trade count, avg tx size, buy/sell ratio).  🌰

        Since Chart.js doesn't natively support subplots, we use multiple y-axes
        on a single chart with toggleable datasets — this preserves the unified
        time-axis alignment that the original matplotlib 4-subplot layout provided.
        """
        timestamps = self._iso_timestamps(data)

        metrics = [
            ("volume",              "Volume",             "rgba(54,162,235,0.9)", "y"),
            ("tradecount",          "Trade Count",        "rgba(75,192,75,0.9)",  "y1"),
            ("avgtransactionsize",  "Avg Transaction Size", "rgba(255,159,64,0.9)", "y2"),
            ("buysellratio",        "Buy/Sell Ratio",     "rgba(255,99,132,0.9)", "y3"),
        ]

        datasets = []
        for col, label, color, yAxisID in metrics:
            datasets.append({
                "label": label,
                "data": data[col].fillna(0).tolist(),
                "borderColor": color,
                "backgroundColor": color.replace("0.9", "0.1"),
                "fill": False,
                "tension": 0.2,
                "pointRadius": 0,
                "yAxisID": yAxisID,
                # Only show first dataset by default — others toggled via legend
                "hidden": yAxisID not in ("y",),
            })

        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": datasets,
            },
            "options": {
                "responsive": True,
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {"display": True, "text": "Cryptocurrency Metrics Over Time"},
                    "legend": {"display": True, "position": "top"},
                    "tooltip": {"enabled": True},
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Timestamp"},
                        "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 20},
                    },
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {"display": True, "text": "Volume"},
                    },
                    "y1": {
                        "type": "linear",
                        "display": False,
                        "position": "left",
                        "grid": {"drawOnChartArea": False},
                        "title": {"display": True, "text": "Trade Count"},
                    },
                    "y2": {
                        "type": "linear",
                        "display": False,
                        "position": "right",
                        "grid": {"drawOnChartArea": False},
                        "title": {"display": True, "text": "Avg Transaction Size"},
                    },
                    "y3": {
                        "type": "linear",
                        "display": False,
                        "position": "right",
                        "grid": {"drawOnChartArea": False},
                        "title": {"display": True, "text": "Buy/Sell Ratio"},
                        "suggestedMin": 0,
                        "suggestedMax": 1,
                    },
                },
            },
        }
        return self._save_json(config, directory, 'crypto_metrics.json')

    def _make_benfordlaw(self, data: pd.DataFrame, directory: str) -> str:
        """Benford's Law test score with dual-axis critical value overlay.  🌰"""
        timestamps = self._iso_timestamps(data)
        benford_scores = data['benfordlawtest'].fillna(0).tolist()
        # K-S critical value at α = 0.05
        critical_values = (1.36 / np.sqrt(
            data['tradecount'].replace(0, 1)
        )).tolist()

        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Benford Law Test Score",
                        "data": benford_scores,
                        "borderColor": "rgba(54,162,235,0.9)",
                        "backgroundColor": "rgba(54,162,235,0.1)",
                        "fill": False,
                        "tension": 0.2,
                        "pointRadius": 0,
                        "yAxisID": "y",
                    },
                    {
                        "label": "K-S Critical Value (α=0.05)",
                        "data": critical_values,
                        "borderColor": "rgba(75,192,75,0.9)",
                        "backgroundColor": "rgba(75,192,75,0.1)",
                        "fill": False,
                        "tension": 0.2,
                        "pointRadius": 0,
                        "borderDash": [6, 4],
                        "yAxisID": "y1",
                    },
                ],
            },
            "options": {
                "responsive": True,
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Benford Law Test Score vs K-S Critical Value",
                    },
                    "tooltip": {"enabled": True},
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Timestamp"},
                        "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 20},
                    },
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {"display": True, "text": "Benford Law Test Score"},
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "grid": {"drawOnChartArea": False},
                        "title": {"display": True, "text": "K-S Critical Value"},
                    },
                },
            },
        }
        return self._save_json(config, directory, 'benford_law.json')

    def _make_vvcorrelation(self, data: pd.DataFrame, directory: str) -> str:
        """Volume–Volatility correlation over time.  🌰"""
        timestamps = self._iso_timestamps(data)
        vv_values = data['vvcorrelation'].fillna(0).tolist()

        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [{
                    "label": "VV Correlation",
                    "data": vv_values,
                    "borderColor": "rgba(128,0,128,0.9)",
                    "backgroundColor": "rgba(128,0,128,0.15)",
                    "fill": True,
                    "tension": 0.2,
                    "pointRadius": 2,
                    "pointHoverRadius": 5,
                }],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Volume–Volatility Correlation Over Time",
                    },
                    "tooltip": {"enabled": True},
                    # 🌰 Suspicion threshold annotation (rendered as a second dataset)
                },
                "scales": {
                    "x": {
                        "title": {"display": True, "text": "Timestamp"},
                        "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 20},
                    },
                    "y": {
                        "title": {"display": True, "text": "VV Correlation"},
                        "suggestedMin": -1,
                        "suggestedMax": 1,
                    },
                },
            },
        }

        # Add suspicion threshold as a flat-line dataset (no plugin dependency)
        n = len(timestamps)
        config["data"]["datasets"].append({
            "label": "Suspicion Threshold (0.4)",
            "data": [0.4] * n,
            "borderColor": "rgba(255,0,0,0.5)",
            "borderDash": [8, 4],
            "borderWidth": 2,
            "pointRadius": 0,
            "fill": False,
        })

        return self._save_json(config, directory, 'vv_correlation.json')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(self, data, directory: str) -> list:
        """Generate all chart JSON files for a market health report.

        Args:
            data: Raw data (list of dicts or DataFrame) from the Market Health API.
            directory: Output directory (Hugo page bundle path).

        Returns:
            List of generated filenames (e.g. ['volume_hist.json', ...]).
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        generated = []
        generated.append(self._make_volume_hist(df, directory))
        generated.append(self._make_crypto_metrics(df, directory))
        generated.append(self._make_benfordlaw(df, directory))
        generated.append(self._make_vvcorrelation(df, directory))

        return generated
