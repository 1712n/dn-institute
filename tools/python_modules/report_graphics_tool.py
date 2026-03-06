"""
🌰 Report Graphics Tool — Dynamic Chart.js shortcode generation 🌰

Replaces static matplotlib PNG generation with interactive Chart.js charts
rendered via Hugo shortcodes. Charts are embedded directly in the markdown
report as Hugo shortcodes with inline JSON data.

Each chart method returns a Hugo shortcode string that can be inserted
into the generated article markdown.
"""

import json
import math
import os
import pandas as pd
import numpy as np


class Visualization:
    """
    🌰 Generates interactive Chart.js chart shortcodes for Market Health reports.

    Instead of saving static PNG files, each method returns a Hugo shortcode
    string using the `metric_chart` shortcode. The chart data is embedded
    as inline JSON, making charts fully interactive in the browser.
    """

    def __init__(self):
        self._chart_counter = 0

    def _next_id(self, prefix="chart"):
        """Generate a unique chart ID 🌰"""
        self._chart_counter += 1
        return f"{prefix}-{self._chart_counter}"

    def _format_shortcode(self, chart_id, chart_type, data, options, caption, height="400"):
        """
        🌰 Format a metric_chart Hugo shortcode string.

        Args:
            chart_id: Unique identifier for the chart
            chart_type: Chart.js chart type (line, bar, scatter, etc.)
            data: Dict with Chart.js data configuration
            options: Dict with Chart.js options configuration
            caption: Caption text for the chart
            height: Canvas height in pixels

        Returns:
            Hugo shortcode string ready for markdown insertion
        """
        data_json = json.dumps(data, separators=(',', ':'))
        options_json = json.dumps(options, separators=(',', ':'))

        return (
            f'{{{{< metric_chart '
            f'id="{chart_id}" '
            f'type="{chart_type}" '
            f"data='{data_json}' "
            f"options='{options_json}' "
            f'caption="{caption}" '
            f'height="{height}" '
            f'>}}}}'
        )

    def _make_volume_hist(self, data):
        """
        🌰 Generate interactive volume distribution histogram.

        Replaces the static volume_hist.png with a dynamic bar chart
        showing transaction volume frequency distribution.
        """
        volumes = data['volume'].dropna().tolist()

        # Compute histogram bins (matching the original 30 bins)
        counts, bin_edges = np.histogram(volumes, bins=30)
        labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(counts))]

        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "Frequency",
                "data": counts.tolist(),
                "backgroundColor": "rgba(135,206,250,0.7)",
                "borderColor": "rgba(0,0,0,0.8)",
                "borderWidth": 1
            }]
        }

        chart_options = {
            "scales": {
                "x": {
                    "title": {"display": True, "text": "Transaction Volume"},
                    "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 10}
                },
                "y": {
                    "title": {"display": True, "text": "Frequency"},
                    "beginAtZero": True
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Transaction Volume Distribution"
                }
            }
        }

        return self._format_shortcode(
            self._next_id("volume-hist"), "bar",
            chart_data, chart_options,
            "Transaction volume distribution — interactive histogram"
        )

    def _make_crypto_metrics(self, data):
        """
        🌰 Generate interactive multi-series crypto metrics chart.

        Shows Volume, Trade Count, Avg Transaction Size, and Buy/Sell Ratio
        over time on a combined chart with dual Y-axes.
        """
        timestamps = [ts.isoformat() if hasattr(ts, 'isoformat') else str(ts) for ts in data.index]

        # Limit label density for readability
        label_step = max(1, len(timestamps) // 20)
        display_labels = [
            timestamps[i] if i % label_step == 0 else ""
            for i in range(len(timestamps))
        ]

        chart_data = {
            "labels": display_labels,
            "datasets": [
                {
                    "label": "Volume",
                    "data": data['volume'].tolist(),
                    "borderColor": "rgba(54,162,235,1)",
                    "backgroundColor": "rgba(54,162,235,0.1)",
                    "fill": True,
                    "tension": 0.3,
                    "pointRadius": 0,
                    "yAxisID": "y"
                },
                {
                    "label": "Trade Count",
                    "data": data['tradecount'].tolist(),
                    "borderColor": "rgba(75,192,75,1)",
                    "backgroundColor": "rgba(75,192,75,0.1)",
                    "fill": True,
                    "tension": 0.3,
                    "pointRadius": 0,
                    "yAxisID": "y"
                },
                {
                    "label": "Avg Transaction Size",
                    "data": data['avgtransactionsize'].tolist(),
                    "borderColor": "rgba(255,159,64,1)",
                    "backgroundColor": "rgba(255,159,64,0.1)",
                    "fill": True,
                    "tension": 0.3,
                    "pointRadius": 0,
                    "yAxisID": "y"
                },
                {
                    "label": "Buy/Sell Ratio",
                    "data": data['buysellratio'].tolist(),
                    "borderColor": "rgba(255,99,132,1)",
                    "backgroundColor": "rgba(255,99,132,0.1)",
                    "fill": True,
                    "tension": 0.3,
                    "pointRadius": 0,
                    "yAxisID": "y2"
                }
            ]
        }

        chart_options = {
            "scales": {
                "x": {
                    "title": {"display": True, "text": "Timestamp"},
                    "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 15}
                },
                "y": {
                    "type": "linear",
                    "position": "left",
                    "title": {"display": True, "text": "Volume / Count / Size"}
                },
                "y2": {
                    "type": "linear",
                    "position": "right",
                    "title": {"display": True, "text": "Buy/Sell Ratio"},
                    "grid": {"drawOnChartArea": False}
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Cryptocurrency Metrics Over Time"
                }
            }
        }

        return self._format_shortcode(
            self._next_id("crypto-metrics"), "line",
            chart_data, chart_options,
            "Key cryptocurrency trading metrics over time — hover for details",
            height="500"
        )

    def _make_benfordlaw(self, data):
        """
        🌰 Generate interactive Benford's Law compliance chart.

        Dual-axis chart showing the K-S test score against the critical
        threshold (1.36 / sqrt(tradecount)) over time.
        """
        timestamps = [ts.isoformat() if hasattr(ts, 'isoformat') else str(ts) for ts in data.index]

        label_step = max(1, len(timestamps) // 20)
        display_labels = [
            timestamps[i] if i % label_step == 0 else ""
            for i in range(len(timestamps))
        ]

        # Calculate critical values: 1.36 / sqrt(tradecount)
        critical_values = [
            round(1.36 / math.sqrt(tc), 6) if tc > 0 else 0
            for tc in data['tradecount'].tolist()
        ]

        chart_data = {
            "labels": display_labels,
            "datasets": [
                {
                    "label": "Benford Law Test Score",
                    "data": data['benfordlawtest'].tolist(),
                    "borderColor": "rgba(54,162,235,1)",
                    "backgroundColor": "rgba(54,162,235,0.1)",
                    "fill": False,
                    "tension": 0.3,
                    "pointRadius": 0,
                    "yAxisID": "y"
                },
                {
                    "label": "Critical Value (1.36/\u221an)",
                    "data": critical_values,
                    "borderColor": "rgba(75,192,75,1)",
                    "backgroundColor": "rgba(75,192,75,0.1)",
                    "borderDash": [5, 5],
                    "fill": False,
                    "tension": 0.3,
                    "pointRadius": 0,
                    "yAxisID": "y2"
                }
            ]
        }

        chart_options = {
            "scales": {
                "x": {
                    "title": {"display": True, "text": "Timestamp"},
                    "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 15}
                },
                "y": {
                    "type": "linear",
                    "position": "left",
                    "title": {"display": True, "text": "Benford Law Test Score"}
                },
                "y2": {
                    "type": "linear",
                    "position": "right",
                    "title": {"display": True, "text": "Critical Value"},
                    "grid": {"drawOnChartArea": False}
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Benford Law Test Score and Critical Threshold Over Time"
                }
            }
        }

        return self._format_shortcode(
            self._next_id("benford-law"), "line",
            chart_data, chart_options,
            "Benford's Law K-S test score vs. critical threshold — values above the threshold indicate non-conformity"
        )

    def _make_vvcorrelation(self, data):
        """
        🌰 Generate interactive volume-volatility correlation chart.

        Line chart showing the VV correlation coefficient over time with
        a reference line at the 0.4 anomaly threshold.
        """
        timestamps = [ts.isoformat() if hasattr(ts, 'isoformat') else str(ts) for ts in data.index]

        label_step = max(1, len(timestamps) // 20)
        display_labels = [
            timestamps[i] if i % label_step == 0 else ""
            for i in range(len(timestamps))
        ]

        # Threshold reference line at 0.4
        threshold_line = [0.4] * len(timestamps)

        chart_data = {
            "labels": display_labels,
            "datasets": [
                {
                    "label": "VV Correlation",
                    "data": data['vvcorrelation'].tolist(),
                    "borderColor": "rgba(128,0,128,1)",
                    "backgroundColor": "rgba(128,0,128,0.1)",
                    "fill": True,
                    "tension": 0.3,
                    "pointRadius": 2,
                    "pointBackgroundColor": "rgba(128,0,128,0.6)"
                },
                {
                    "label": "Anomaly Threshold (0.4)",
                    "data": threshold_line,
                    "borderColor": "rgba(255,0,0,0.5)",
                    "borderDash": [10, 5],
                    "fill": False,
                    "pointRadius": 0,
                    "borderWidth": 2
                }
            ]
        }

        chart_options = {
            "scales": {
                "x": {
                    "title": {"display": True, "text": "Timestamp"},
                    "ticks": {"maxRotation": 45, "autoSkip": True, "maxTicksLimit": 15}
                },
                "y": {
                    "title": {"display": True, "text": "VV Correlation Coefficient"},
                    "suggestedMin": -0.5,
                    "suggestedMax": 1.0
                }
            },
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Volume-Volatility Correlation Over Time"
                }
            }
        }

        return self._format_shortcode(
            self._next_id("vv-correlation"), "line",
            chart_data, chart_options,
            "Volume-volatility correlation — values consistently below 0.4 suggest artificial trading volume"
        )

    def generate_report(self, data, directory):
        """
        🌰 Generate interactive chart shortcodes from market health data.

        Instead of saving static PNGs to the directory, this method returns
        a dict mapping chart names to their Hugo shortcode strings. These
        shortcodes are also saved to a markdown fragment file for easy
        inclusion in the generated article.

        Args:
            data: Raw market health API response (list of dicts or DataFrame)
            directory: Output directory for the shortcode fragment file

        Returns:
            dict mapping chart names to Hugo shortcode strings
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        if isinstance(data, list):
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        elif isinstance(data, pd.DataFrame):
            df = data
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
        else:
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

        # 🌰 Generate all chart shortcodes
        charts = {}
        charts['volume_hist'] = self._make_volume_hist(df)
        charts['crypto_metrics'] = self._make_crypto_metrics(df)
        charts['benford_law'] = self._make_benfordlaw(df)
        charts['vv_correlation'] = self._make_vvcorrelation(df)

        # Save shortcodes to a fragment file for reference 🌰
        fragment_path = os.path.join(directory, 'chart_shortcodes.md')
        with open(fragment_path, 'w', encoding='utf-8') as f:
            f.write("<!-- 🌰 Auto-generated interactive chart shortcodes 🌰 -->\n\n")
            for name, shortcode in charts.items():
                f.write(f"<!-- {name} -->\n{shortcode}\n\n")

        print(f"🌰 Chart shortcodes saved to: {fragment_path}")
        return charts
