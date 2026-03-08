"""
Visualization tool for Market Health Reporter.

Generates interactive Chart.js charts via Hugo shortcodes instead of static
matplotlib PNG images.  Each chart method returns a Hugo shortcode block
with the chart data serialized as inline JSON.  ``generate_report()``
returns the combined shortcode markdown **and** appends it to the article
``index.md`` located in *directory*.

Chart types produced
--------------------
1. Volume histogram -- transaction volume distribution
2. Crypto metrics -- multi-panel time-series (volume, trade count,
   avg transaction size, buy/sell ratio)
3. Benford law -- test score vs. critical-value threshold over time
4. Volume-volatility correlation -- VV correlation over time
"""

import json
import os
import glob
import math


class Visualization:
    """Generate Hugo metric_chart shortcode blocks from market data."""

    def __init__(self):
        pass

    @staticmethod
    def _fmt_ts(ts_list):
        """Shorten ISO timestamps to YYYY-MM-DD HH:MM strings."""
        out = []
        for ts in ts_list:
            s = str(ts)
            if "T" in s:
                s = s.replace("T", " ")
            out.append(s[:16])
        return out

    @staticmethod
    def _shortcode(chart_id, chart_type, title, data_dict, caption="", height=400):
        """Return a metric_chart shortcode block."""
        inner_json = json.dumps(data_dict, separators=(",", ":"))
        head = "{{< metric_chart" + ' id="' + chart_id + '" type="' + chart_type + '" ' + 'title="' + title + '" height="' + str(height) + '" ' + 'caption="' + caption + '" >}}' 
        return "\n".join([head, inner_json, "{{< /metric_chart >}}"])

    def _make_volume_hist(self, data):
        volumes = [row.get("volume", 0) for row in data]
        if not volumes:
            return ""
        vmin, vmax = min(volumes), max(volumes)
        if vmax == vmin:
            vmax = vmin + 1
        n_bins = 30
        bin_width = (vmax - vmin) / n_bins
        counts = [0] * n_bins
        for v in volumes:
            idx = int((v - vmin) / bin_width)
            if idx >= n_bins:
                idx = n_bins - 1
            counts[idx] += 1
        labels = ["{:.2f}".format(vmin + i * bin_width) for i in range(n_bins)]
        chart_data = {
            "labels": labels,
            "datasets": [{"label": "Frequency", "data": counts,
                "backgroundColor": "rgba(135,206,235,0.7)",
                "borderColor": "rgba(0,0,0,0.8)", "borderWidth": 1}],
            "options": {"scales": {
                "x": {"title": {"display": True, "text": "Transaction Volume"}},
                "y": {"title": {"display": True, "text": "Frequency"}}}},
        }
        return self._shortcode("volume-hist", "bar", "Transaction Volume Distribution",
            chart_data, caption="Histogram of trade volume distribution")

    def _make_crypto_metrics(self, data):
        timestamps = self._fmt_ts([r.get("timestamp", "") for r in data])
        series = [
            ("volume",             "Volume",               "rgba(54,162,235,0.8)"),
            ("tradecount",         "Trade Count",          "rgba(75,192,75,0.8)"),
            ("avgtransactionsize", "Avg Transaction Size", "rgba(255,159,64,0.8)"),
            ("buysellratio",       "Buy/Sell Ratio",       "rgba(255,99,132,0.8)"),
        ]
        blocks = []
        for key, label, color in series:
            values = [row.get(key, 0) for row in data]
            chart_data = {
                "labels": timestamps,
                "datasets": [{"label": label, "data": values,
                    "borderColor": color,
                    "backgroundColor": color.replace("0.8", "0.15"),
                    "fill": True, "pointRadius": 0, "tension": 0.2}],
            }
            blocks.append(self._shortcode("metric-" + key, "line",
                label + " Over Time", chart_data, height=280))
        return "\n\n".join(blocks)

    def _make_benfordlaw(self, data):
        timestamps = self._fmt_ts([r.get("timestamp", "") for r in data])
        benford_scores = [row.get("benfordlawtest", 0) for row in data]
        trade_counts = [row.get("tradecount", 1) for row in data]
        critical_values = [1.36 / math.sqrt(max(tc, 1)) for tc in trade_counts]
        chart_data = {
            "labels": timestamps,
            "datasets": [
                {"label": "Benford Law Test Score", "data": benford_scores,
                 "borderColor": "rgba(54,162,235,1)", "yAxisID": "y",
                 "pointRadius": 0, "tension": 0.2},
                {"label": "Critical Value (1.36/sqrt(n))", "data": critical_values,
                 "borderColor": "rgba(75,192,75,1)", "borderDash": [5, 5],
                 "yAxisID": "y2", "pointRadius": 0, "tension": 0.2},
            ],
            "options": {"scales": {
                "y":  {"position": "left",  "title": {"display": True, "text": "Benford Score"}},
                "y2": {"position": "right", "title": {"display": True, "text": "Critical Value"},
                       "grid": {"drawOnChartArea": False}}}},
        }
        return self._shortcode("benford-law", "line",
            "Benford Law Test Score and Critical Value Over Time", chart_data,
            caption="Scores above the critical value indicate potential data anomalies")

    def _make_vvcorrelation(self, data):
        timestamps = self._fmt_ts([r.get("timestamp", "") for r in data])
        vv_values = [row.get("vvcorrelation", 0) for row in data]
        chart_data = {
            "labels": timestamps,
            "datasets": [{"label": "VV Correlation", "data": vv_values,
                "borderColor": "rgba(128,0,128,1)",
                "backgroundColor": "rgba(128,0,128,0.15)",
                "fill": True, "pointRadius": 2, "tension": 0.2}],
            "options": {"scales": {"y": {"title": {"display": True, "text": "VV Correlation"}}}},
        }
        return self._shortcode("vv-correlation", "line",
            "Volume-Volatility Correlation Over Time", chart_data,
            caption="Correlation between trading volume and price volatility")

    def generate_report(self, data, directory):
        """Generate all chart shortcodes and append to index.md.

        Parameters
        ----------
        data : list[dict]
            Raw market data records from the Market Health API.
        directory : str
            Path to the Hugo article directory containing index.md.

        Returns
        -------
        str
            Combined shortcode markdown for all charts.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        if hasattr(data, "to_dict"):
            records = data.to_dict(orient="records")
        elif isinstance(data, dict):
            keys = list(data.keys())
            if keys and isinstance(data[keys[0]], list):
                length = len(data[keys[0]])
                records = [{k: data[k][i] for k in keys} for i in range(length)]
            else:
                records = [data]
        else:
            records = list(data)

        blocks = [
            self._make_volume_hist(records),
            self._make_crypto_metrics(records),
            self._make_benfordlaw(records),
            self._make_vvcorrelation(records),
        ]
        shortcode_md = "\n\n".join(b for b in blocks if b)

        md_files = glob.glob(os.path.join(directory, "index*.md"))
        if md_files:
            target = md_files[0]
            with open(target, "a", encoding="utf-8") as f:
                f.write("\n\n<!-- Dynamic charts generated by Market Health Reporter -->\n")
                f.write(shortcode_md)
                f.write("\n")
            print("Charts appended to: " + target)

        return shortcode_md
