"""
report_graphics_tool.py — Generates interactive Chart.js charts via Hugo shortcodes.

Replaces the previous matplotlib-based static PNG generation with dynamic,
browser-rendered charts using the {{< metric_chart >}} Hugo shortcode.
Each method returns a shortcode markdown string that can be embedded directly
in the generated article.

The generate_report() method returns the full set of chart shortcodes as a
string, and also injects them into the article markdown file if it exists.
"""

import json
import os
import re
import math
import pandas as pd


class Visualization:
    """Generate interactive Chart.js chart shortcodes for market health reports."""

    def __init__(self):
        pass

    @staticmethod
    def _format_timestamps(timestamps):
        """Format pandas timestamps to short readable strings."""
        return [t.strftime("%b %d %H:%M") for t in timestamps]

    def _make_volume_hist(self, data):
        """Generate a volume distribution histogram shortcode."""
        volumes = data["volume"].dropna().tolist()
        # Create histogram bins
        num_bins = 30
        min_v, max_v = min(volumes), max(volumes)
        bin_width = (max_v - min_v) / num_bins if max_v != min_v else 1
        bins = [0] * num_bins
        for v in volumes:
            idx = min(int((v - min_v) / bin_width), num_bins - 1)
            bins[idx] += 1
        labels = [f"{min_v + i * bin_width:.1f}" for i in range(num_bins)]

        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "Transaction Volume Frequency",
                "data": bins,
                "backgroundColor": "rgba(135, 206, 235, 0.7)",
                "borderColor": "rgba(0, 0, 0, 0.8)",
                "borderWidth": 1,
            }],
        }
        return (
            '{{< metric_chart id="volume-hist" type="bar" '
            'title="Transaction Volume Distribution" '
            'caption="Distribution of transaction volumes over the analysis period" >}}\n'
            f"{json.dumps(chart_data)}\n"
            "{{< /metric_chart >}}"
        )

    def _make_crypto_metrics(self, data):
        """Generate a multi-metric time series chart shortcode."""
        timestamps = self._format_timestamps(data.index)
        chart_data = {
            "labels": timestamps,
            "datasets": [
                {
                    "label": "Volume",
                    "data": data["volume"].tolist(),
                    "borderColor": "rgb(54, 162, 235)",
                    "yAxisID": "y",
                },
                {
                    "label": "Trade Count",
                    "data": data["tradecount"].tolist(),
                    "borderColor": "rgb(75, 192, 192)",
                    "yAxisID": "y1",
                },
                {
                    "label": "Avg Transaction Size",
                    "data": data["avgtransactionsize"].tolist(),
                    "borderColor": "rgb(255, 159, 64)",
                    "yAxisID": "y2",
                },
                {
                    "label": "Buy/Sell Ratio",
                    "data": data["buysellratio"].tolist(),
                    "borderColor": "rgb(255, 99, 132)",
                    "yAxisID": "y3",
                },
            ],
        }
        return (
            '{{< metric_chart id="crypto-metrics" type="line" '
            'title="Cryptocurrency Metrics Over Time" '
            'caption="Volume, trade count, average transaction size, and buy/sell ratio" >}}\n'
            f"{json.dumps(chart_data)}\n"
            "{{< /metric_chart >}}"
        )

    def _make_benfordlaw(self, data):
        """Generate a Benford's Law test chart shortcode."""
        timestamps = self._format_timestamps(data.index)
        # Calculate critical values: 1.36 / sqrt(tradecount)
        critical_values = [
            1.36 / math.sqrt(tc) if tc > 0 else 0
            for tc in data["tradecount"].tolist()
        ]
        chart_data = {
            "labels": timestamps,
            "datasets": [
                {
                    "label": "Benford Law Test Score",
                    "data": data["benfordlawtest"].tolist(),
                    "borderColor": "rgb(54, 162, 235)",
                    "yAxisID": "y",
                },
                {
                    "label": "Critical Value (1.36/sqrt(n))",
                    "data": critical_values,
                    "borderColor": "rgb(75, 192, 192)",
                    "borderDash": [5, 5],
                    "yAxisID": "y",
                },
            ],
        }
        return (
            '{{< metric_chart id="benford-law" type="line" '
            'title="Benford Law Test Score Over Time" '
            'caption="Benford Law test statistic vs. critical value threshold" >}}\n'
            f"{json.dumps(chart_data)}\n"
            "{{< /metric_chart >}}"
        )

    def _make_vvcorrelation(self, data):
        """Generate a volume-volatility correlation chart shortcode."""
        timestamps = self._format_timestamps(data.index)
        chart_data = {
            "labels": timestamps,
            "datasets": [{
                "label": "Volume-Volatility Correlation",
                "data": data["vvcorrelation"].tolist(),
                "borderColor": "rgb(153, 102, 255)",
                "backgroundColor": "rgba(153, 102, 255, 0.1)",
                "fill": True,
            }],
        }
        return (
            '{{< metric_chart id="vv-correlation" type="line" '
            'title="Volume-Volatility Correlation Over Time" '
            'caption="Correlation between trading volume and price volatility" >}}\n'
            f"{json.dumps(chart_data)}\n"
            "{{< /metric_chart >}}"
        )

    def generate_report(self, data, directory):
        """
        Generate interactive chart shortcodes and inject them into the article.

        Args:
            data: Raw API response data (list of dicts or dict with lists).
            directory: Path to the article output directory.

        Returns:
            str: Combined shortcode markdown for all charts.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        charts = []
        charts.append(self._make_volume_hist(df))
        charts.append(self._make_crypto_metrics(df))
        if "benfordlawtest" in df.columns:
            charts.append(self._make_benfordlaw(df))
        if "vvcorrelation" in df.columns:
            charts.append(self._make_vvcorrelation(df))

        chart_block = "\n\n".join(charts)

        # Inject charts into the article markdown if it exists
        # Append charts section before the end of the article
        index_files = [
            f for f in os.listdir(directory)
            if f.startswith("index") and f.endswith(".md")
        ]
        if index_files:
            article_path = os.path.join(directory, index_files[-1])
            with open(article_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Append interactive charts section if not already present
            if "metric_chart" not in content:
                content += f"\n\n## Interactive Charts\n\n{chart_block}\n"
                with open(article_path, "w", encoding="utf-8") as f:
                    f.write(content)

        return chart_block
