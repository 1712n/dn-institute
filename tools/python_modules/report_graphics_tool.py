import json
import os

import numpy as np
import pandas as pd


class Visualization:
    """Generate interactive Chart.js charts via Hugo shortcodes.

    Instead of saving static matplotlib PNGs, each chart method returns a Hugo
    shortcode string that embeds the chart data as inline JSON. The shortcode
    ``market_chart`` (layouts/shortcodes/market_chart.html) renders these as
    interactive, responsive Chart.js charts in the browser.
    """

    def __init__(self):
        pass

    @staticmethod
    def _ts_labels(index):
        """Convert a DatetimeIndex to ISO-formatted string labels."""
        return [t.strftime("%Y-%m-%d %H:%M") for t in index]

    def _make_volume_hist(self, data):
        """Return a Hugo shortcode for an interactive volume histogram."""
        volumes = data["volume"].dropna().values
        counts, bin_edges = np.histogram(volumes, bins=30)
        labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(counts))]
        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Frequency",
                    "data": counts.tolist(),
                    "backgroundColor": "rgba(135,206,235,0.7)",
                    "borderColor": "rgba(0,0,0,0.8)",
                    "borderWidth": 1,
                }
            ],
        }
        inner = json.dumps(chart_data)
        return (
            '{{< market_chart id="volume-hist" type="bar" '
            'title="Transaction Volume Distribution" '
            'xLabel="Transaction Volume" yLabel="Frequency" >}}\n'
            f"{inner}\n"
            "{{< /market_chart >}}"
        )

    def _make_crypto_metrics(self, data):
        """Return Hugo shortcodes for each crypto metric as separate line charts."""
        labels = self._ts_labels(data.index)
        metrics = [
            ("volume", "Volume", "rgba(54,162,235,1)"),
            ("tradecount", "Trade Count", "rgba(75,192,75,1)"),
            ("avgtransactionsize", "Avg Transaction Size", "rgba(255,159,64,1)"),
            ("buysellratio", "Buy/Sell Ratio", "rgba(255,99,132,1)"),
        ]
        shortcodes = []
        for col, label, color in metrics:
            if col not in data.columns:
                continue
            chart_data = {
                "labels": labels,
                "datasets": [
                    {
                        "label": label,
                        "data": data[col].tolist(),
                        "borderColor": color,
                        "backgroundColor": color.replace("1)", "0.1)"),
                        "fill": True,
                        "tension": 0.2,
                        "pointRadius": 0,
                    }
                ],
            }
            inner = json.dumps(chart_data)
            slug = col.replace(" ", "-").lower()
            shortcodes.append(
                f'{{{{< market_chart id="metric-{slug}" type="line" '
                f'title="{label} Over Time" '
                f'xLabel="Timestamp" yLabel="{label}" >}}}}\n'
                f"{inner}\n"
                "{{< /market_chart >}}"
            )
        return "\n\n".join(shortcodes)

    def _make_benfordlaw(self, data):
        """Return a Hugo shortcode for a dual-axis Benford law chart."""
        labels = self._ts_labels(data.index)
        benford_vals = data["benfordlawtest"].tolist()
        threshold = (1.36 / np.sqrt(data["tradecount"])).tolist()
        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Benford Law Test Score",
                    "data": benford_vals,
                    "borderColor": "rgba(54,162,235,1)",
                    "backgroundColor": "rgba(54,162,235,0.1)",
                    "fill": False,
                    "tension": 0.2,
                    "pointRadius": 0,
                    "yAxisID": "y",
                },
                {
                    "label": "Critical Value (1.36/sqrt(n))",
                    "data": threshold,
                    "borderColor": "rgba(75,192,75,1)",
                    "backgroundColor": "rgba(75,192,75,0.1)",
                    "fill": False,
                    "tension": 0.2,
                    "pointRadius": 0,
                    "yAxisID": "y2",
                },
            ],
        }
        inner = json.dumps(chart_data)
        return (
            '{{< market_chart id="benford-law" type="line" '
            'title="Benford Law Test Score and Trade Count Over Time" '
            'xLabel="Timestamp" yLabel="Benford Law Test Score" '
            'y2Label="Critical Value" >}}\n'
            f"{inner}\n"
            "{{< /market_chart >}}"
        )

    def _make_vvcorrelation(self, data):
        """Return a Hugo shortcode for a VV correlation line chart."""
        labels = self._ts_labels(data.index)
        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "VV Correlation",
                    "data": data["vvcorrelation"].tolist(),
                    "borderColor": "rgba(128,0,128,1)",
                    "backgroundColor": "rgba(128,0,128,0.1)",
                    "fill": True,
                    "tension": 0.2,
                    "pointRadius": 2,
                }
            ],
        }
        inner = json.dumps(chart_data)
        return (
            '{{< market_chart id="vv-correlation" type="line" '
            'title="VV Correlation Over Time" '
            'xLabel="Timestamp" yLabel="VV Correlation" >}}\n'
            f"{inner}\n"
            "{{< /market_chart >}}"
        )

    def generate_report(self, data, directory):
        """Generate interactive Chart.js shortcodes from market data.

        Returns a string of Hugo shortcodes. Also writes them to
        ``charts.md`` in *directory* for easy inclusion in reports.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        sections = []
        sections.append(self._make_volume_hist(df))
        sections.append(self._make_crypto_metrics(df))
        if "benfordlawtest" in df.columns and "tradecount" in df.columns:
            sections.append(self._make_benfordlaw(df))
        if "vvcorrelation" in df.columns:
            sections.append(self._make_vvcorrelation(df))

        shortcodes = "\n\n".join(sections)

        charts_path = os.path.join(directory, "charts.md")
        with open(charts_path, "w", encoding="utf-8") as f:
            f.write(shortcodes)

        return shortcodes
