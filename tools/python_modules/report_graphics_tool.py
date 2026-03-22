"""
report_graphics_tool.py — Generate interactive Chart.js charts via Hugo shortcodes.

Replaces the previous matplotlib-based static PNG generation with dynamic,
browser-rendered charts using the ``{{< metric_chart >}}`` Hugo shortcode.

Each chart method produces a Hugo shortcode string with an embedded JSON config
that the metric-charts.js module will parse at render time.  The JSON contains
the Chart.js *type*, *data*, an optional *title*, and any extra *options*
(e.g. multi-axis scales, threshold annotations).

The public interface (``Visualization.generate_report(data, directory)``)
remains unchanged so the existing ``market_health_reporter.py`` pipeline
works without modification.
"""

import json
import math
import os
import re

import pandas as pd


class Visualization:
    """Generate interactive Chart.js chart shortcodes for market health reports."""

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fmt_ts(timestamps):
        """Format a DatetimeIndex to short human-readable labels."""
        return [t.strftime("%Y-%m-%d %H:%M") for t in timestamps]

    @staticmethod
    def _shortcode(chart_id, config, caption=""):
        """Wrap a Chart.js config dict into a Hugo metric_chart shortcode."""
        caption_attr = f' caption="{caption}"' if caption else ""
        inner = json.dumps(config, default=str)
        return (
            f'{{{{< metric_chart id="{chart_id}"{caption_attr} >}}}}\n'
            f"{inner}\n"
            "{{< /metric_chart >}}"
        )

    # ------------------------------------------------------------------
    # Chart builders
    # ------------------------------------------------------------------

    def _make_volume_hist(self, data):
        """Transaction volume distribution histogram."""
        volumes = data["volume"].dropna().tolist()
        num_bins = 30
        min_v = min(volumes) if volumes else 0
        max_v = max(volumes) if volumes else 1
        bin_width = (max_v - min_v) / num_bins if max_v != min_v else 1

        bins = [0] * num_bins
        for v in volumes:
            idx = min(int((v - min_v) / bin_width), num_bins - 1)
            bins[idx] += 1

        labels = [f"{min_v + i * bin_width:.0f}" for i in range(num_bins)]

        config = {
            "type": "bar",
            "title": "Transaction Volume Distribution",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Frequency",
                        "data": bins,
                        "backgroundColor": "rgba(135, 206, 235, 0.7)",
                        "borderColor": "rgba(0, 0, 0, 0.3)",
                        "borderWidth": 1,
                    }
                ],
            },
            "options": {
                "scales": {
                    "x": {"title": {"display": True, "text": "Transaction Volume"}},
                    "y": {"title": {"display": True, "text": "Frequency"}},
                }
            },
        }
        return self._shortcode(
            "volume-hist",
            config,
            caption="Distribution of transaction volumes over the analysis period",
        )

    def _make_crypto_metrics(self, data):
        """Multi-panel time-series: volume, trade count, avg tx size, buy/sell ratio.

        Uses four independent Y axes so that each metric has its own scale,
        matching the original four-subplot matplotlib layout.
        """
        labels = self._fmt_ts(data.index)

        config = {
            "type": "line",
            "title": "Cryptocurrency Metrics Over Time",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Volume",
                        "data": data["volume"].tolist(),
                        "borderColor": "rgb(54, 162, 235)",
                        "yAxisID": "yVolume",
                    },
                    {
                        "label": "Trade Count",
                        "data": data["tradecount"].tolist(),
                        "borderColor": "rgb(75, 192, 192)",
                        "yAxisID": "yTradeCount",
                    },
                    {
                        "label": "Avg Transaction Size",
                        "data": data["avgtransactionsize"].tolist(),
                        "borderColor": "rgb(255, 159, 64)",
                        "yAxisID": "yAvgTx",
                    },
                    {
                        "label": "Buy/Sell Ratio",
                        "data": data["buysellratio"].tolist(),
                        "borderColor": "rgb(255, 99, 132)",
                        "yAxisID": "yBSR",
                    },
                ],
            },
            "options": {
                "interaction": {"mode": "index", "intersect": False},
                "scales": {
                    "yVolume": {
                        "type": "linear",
                        "position": "left",
                        "title": {"display": True, "text": "Volume"},
                        "grid": {"drawOnChartArea": True},
                    },
                    "yTradeCount": {
                        "type": "linear",
                        "position": "left",
                        "title": {"display": True, "text": "Trade Count"},
                        "grid": {"drawOnChartArea": False},
                    },
                    "yAvgTx": {
                        "type": "linear",
                        "position": "right",
                        "title": {"display": True, "text": "Avg Tx Size"},
                        "grid": {"drawOnChartArea": False},
                    },
                    "yBSR": {
                        "type": "linear",
                        "position": "right",
                        "title": {"display": True, "text": "Buy/Sell Ratio"},
                        "grid": {"drawOnChartArea": False},
                    },
                },
            },
        }
        return self._shortcode(
            "crypto-metrics",
            config,
            caption="Volume, trade count, average transaction size, and buy/sell ratio over time",
        )

    def _make_benfordlaw(self, data):
        """Benford's Law K-S test score vs critical threshold over time.

        The critical value is ``1.36 / sqrt(tradecount)``; data points above
        this threshold indicate deviation from Benford's Law.
        """
        labels = self._fmt_ts(data.index)
        benford_scores = data["benfordlawtest"].tolist()
        critical_values = [
            round(1.36 / math.sqrt(tc), 6) if tc > 0 else 0
            for tc in data["tradecount"].tolist()
        ]

        config = {
            "type": "line",
            "title": "Benford's Law Test: K-S Statistic vs Critical Value",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "K-S Test Statistic",
                        "data": benford_scores,
                        "borderColor": "rgb(54, 162, 235)",
                    },
                    {
                        "label": "Critical Value (1.36/\u221an)",
                        "data": critical_values,
                        "borderColor": "rgb(255, 99, 132)",
                        "borderDash": [6, 3],
                    },
                ],
            },
            "options": {
                "interaction": {"mode": "index", "intersect": False},
                "scales": {
                    "y": {
                        "title": {"display": True, "text": "Statistic Value"},
                    },
                },
            },
        }
        return self._shortcode(
            "benford-law",
            config,
            caption="K-S test statistic vs critical value; points above the threshold "
            "indicate deviation from Benford's Law",
        )

    def _make_vvcorrelation(self, data):
        """Volume-volatility correlation over time.

        Low correlation (below ~0.4) over extended periods suggests artificial
        volume that does not impact price discovery.
        """
        labels = self._fmt_ts(data.index)
        vv_values = data["vvcorrelation"].tolist()

        # Add a reference threshold line at 0.4
        threshold = [0.4] * len(labels)

        config = {
            "type": "line",
            "title": "Volume-Volatility Correlation Over Time",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "VV Correlation",
                        "data": vv_values,
                        "borderColor": "rgb(153, 102, 255)",
                        "backgroundColor": "rgba(153, 102, 255, 0.1)",
                        "fill": True,
                    },
                    {
                        "label": "Anomaly Threshold (0.4)",
                        "data": threshold,
                        "borderColor": "rgba(255, 99, 132, 0.6)",
                        "borderDash": [6, 3],
                        "borderWidth": 1,
                        "pointRadius": 0,
                        "fill": False,
                    },
                ],
            },
            "options": {
                "scales": {
                    "y": {
                        "title": {"display": True, "text": "Correlation Coefficient"},
                        "suggestedMin": -1,
                        "suggestedMax": 1,
                    },
                },
            },
        }
        return self._shortcode(
            "vv-correlation",
            config,
            caption="Correlation between trading volume and price volatility; "
            "values persistently below 0.4 suggest artificial volume",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(self, data, directory):
        """Generate interactive chart shortcodes and inject them into the article.

        Maintains the same public interface as the previous matplotlib version.

        Args:
            data: Raw API response data (list of dicts or dict-of-lists).
            directory: Path to the article output directory.

        Returns:
            str: Combined shortcode markdown for all generated charts.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        charts = [self._make_volume_hist(df), self._make_crypto_metrics(df)]

        if "benfordlawtest" in df.columns:
            charts.append(self._make_benfordlaw(df))

        if "vvcorrelation" in df.columns:
            charts.append(self._make_vvcorrelation(df))

        chart_block = "\n\n".join(charts)

        # Inject charts into the article markdown if it exists in the directory
        index_files = sorted(
            [
                f
                for f in os.listdir(directory)
                if f.startswith("index") and f.endswith(".md")
            ]
        )
        if index_files:
            article_path = os.path.join(directory, index_files[-1])
            with open(article_path, "r", encoding="utf-8") as fh:
                content = fh.read()

            # Build a map of placeholder patterns to chart shortcodes.
            # Supports three formats:
            #   1. Old static PNG figure shortcodes (backward compat)
            #   2. New <!-- CHART: name --> HTML comment placeholders
            #   3. Bare PNG filenames referenced in any shortcode
            chart_map = {
                "volume_hist": charts[0],
                "crypto_metrics": charts[1],
            }
            if len(charts) > 2:
                chart_map["benford_law"] = charts[2]
            if len(charts) > 3:
                chart_map["vv_correlation"] = charts[3]

            modified = False
            for name, shortcode in chart_map.items():
                # Replace {{< figure src="<name>.png" ... >}}
                pattern_fig = (
                    r'\{\{<\s*figure\s+[^>]*src="' + re.escape(name) + r'\.png"[^>]*>\}\}'
                )
                new_content = re.sub(pattern_fig, shortcode, content)
                if new_content != content:
                    content = new_content
                    modified = True

                # Replace <!-- CHART: <name> -->
                pattern_comment = r'<!--\s*CHART:\s*' + re.escape(name) + r'\s*-->'
                new_content = re.sub(pattern_comment, shortcode, content)
                if new_content != content:
                    content = new_content
                    modified = True

            # If no replacements were made (article doesn't reference PNGs),
            # append charts section
            if not modified and "metric_chart" not in content:
                content += f"\n\n## Interactive Charts\n\n{chart_block}\n"
                modified = True

            if modified:
                with open(article_path, "w", encoding="utf-8") as fh:
                    fh.write(content)

        return chart_block
