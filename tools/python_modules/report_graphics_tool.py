"""
report_graphics_tool.py — Dynamic chart generation for Market Health Reporter.

Replaces static matplotlib PNG generation with interactive Apache ECharts charts
embedded in Hugo articles via the {{< echarts >}} shortcode.

🌰 Zero dependencies on matplotlib, pandas, or numpy.
"""

import os
import json


class Visualization:
    """
    Generates Hugo ``echarts`` shortcode blocks from raw market data dicts.

    Each method returns a markdown string (one or more shortcode blocks) that
    Hugo renders as interactive Apache ECharts charts.  The ``generate_report``
    method writes all charts to the article ``index.md`` in the given directory.

    Why ECharts?
    - Native financial chart types (candlestick, OHLC) — ideal for market data
    - Built-in zoom / pan / export toolbox — no extra JS needed
    - Dark-mode aware via theme detection in the shortcode
    - Smaller bundle footprint via jsDelivr CDN (loaded once per page)
    - 🌰 Chestnut-overlord approved
    """

    def __init__(self):
        pass

    @staticmethod
    def _shortcode(chart_id: str, option: dict, title: str = "",
                   height: int = 400, caption: str = "") -> str:
        """Wrap an ECharts option dict in a Hugo shortcode block."""
        params = [f'id="{chart_id}"']
        if title:
            params.append(f'title="{title}"')
        if height != 400:
            params.append(f'height="{height}"')
        if caption:
            params.append(f'caption="{caption}"')

        option_json = json.dumps(option, ensure_ascii=False, separators=(',', ':'))
        return f'{{{{< echarts {" ".join(params)} >}}}}\n{option_json}\n{{{{< /echarts >}}}}\n'

    @staticmethod
    def _timestamps(data: list[dict]) -> list[str]:
        return [str(row.get("timestamp", "")) for row in data]

    def _make_volume_hist(self, data: list[dict]) -> str:
        """
        Transaction-volume histogram using ECharts bar chart with auto-binning.
        🌰 Pure Python — no numpy required.
        """
        volumes = [float(row["volume"]) for row in data if row.get("volume") is not None]
        if not volumes:
            return ""

        bins = 30
        min_v, max_v = min(volumes), max(volumes)
        if max_v == min_v:
            return ""
        bin_width = (max_v - min_v) / bins

        counts = [0] * bins
        for v in volumes:
            idx = min(int((v - min_v) / bin_width), bins - 1)
            counts[idx] += 1

        labels = [f"{min_v + i * bin_width:.2f}" for i in range(bins)]

        option = {
            "xAxis": {
                "type": "category",
                "data": labels,
                "name": "Transaction Volume",
                "nameLocation": "middle",
                "nameGap": 35,
                "axisLabel": {"rotate": 30}
            },
            "yAxis": {"type": "value", "name": "Frequency"},
            "series": [{
                "type": "bar",
                "data": counts,
                "itemStyle": {"color": "rgba(135,206,235,0.85)", "borderColor": "#000", "borderWidth": 0.5},
                "barMaxWidth": "95%"
            }]
        }
        return self._shortcode(
            "volume-hist", option,
            title="🌰 Transaction Volume Distribution",
            caption="30-bin histogram of transaction volumes"
        )

    def _make_crypto_metrics(self, data: list[dict]) -> str:
        """
        Four time-series charts in separate shortcode blocks:
        volume, trade count, average transaction size, buy/sell ratio.
        🌰 ECharts line charts with zoom/pan toolbox.
        """
        timestamps = self._timestamps(data)
        blocks = []

        series_configs = [
            ("volume",             "Volume",                "#5470c6", "volume-ts",         "🌰 Volume Over Time"),
            ("tradecount",         "Trade Count",           "#91cc75", "tradecount-ts",      "🌰 Trade Count Over Time"),
            ("avgtransactionsize", "Avg Transaction Size",  "#fac858", "avgtxsize-ts",       "🌰 Average Transaction Size Over Time"),
            ("buysellratio",       "Buy / Sell Ratio",      "#ee6666", "buysellratio-ts",    "🌰 Buy/Sell Ratio Over Time"),
        ]

        for field, label, color, chart_id, title in series_configs:
            values = [row.get(field) for row in data]
            if all(v is None for v in values):
                continue
            option = {
                "xAxis": {
                    "type": "category",
                    "data": timestamps,
                    "axisLabel": {"rotate": 30}
                },
                "yAxis": {"type": "value", "name": label},
                "series": [{
                    "name": label,
                    "type": "line",
                    "data": values,
                    "lineStyle": {"color": color},
                    "itemStyle": {"color": color},
                    "showSymbol": False,
                    "smooth": True,
                    "areaStyle": {"opacity": 0.1}
                }]
            }
            blocks.append(self._shortcode(chart_id, option, title=title, height=300))

        return "\n".join(blocks)

    def _make_benfordlaw(self, data: list[dict]) -> str:
        """
        Benford law test score vs. critical value (1.36/√N) — dual y-axis ECharts line chart.
        🌰 Pure Python sqrt — no numpy required.
        """
        timestamps = self._timestamps(data)
        scores = [row.get("benfordlawtest") for row in data]
        tradecounts = [row.get("tradecount") for row in data]

        critical_values = []
        for tc in tradecounts:
            if tc and float(tc) > 0:
                critical_values.append(round(1.36 / (float(tc) ** 0.5), 6))
            else:
                critical_values.append(None)

        option = {
            "xAxis": {
                "type": "category",
                "data": timestamps,
                "axisLabel": {"rotate": 30}
            },
            "yAxis": [
                {"type": "value", "name": "Benford Score", "position": "left"},
                {
                    "type": "value",
                    "name": "Critical Value",
                    "position": "right",
                    "splitLine": {"show": False}
                }
            ],
            "series": [
                {
                    "name": "Benford Law Score",
                    "type": "line",
                    "yAxisIndex": 0,
                    "data": scores,
                    "lineStyle": {"color": "#5470c6"},
                    "itemStyle": {"color": "#5470c6"},
                    "showSymbol": False,
                    "smooth": True
                },
                {
                    "name": "Critical Value (1.36/√N)",
                    "type": "line",
                    "yAxisIndex": 1,
                    "data": critical_values,
                    "lineStyle": {"color": "#91cc75", "type": "dashed"},
                    "itemStyle": {"color": "#91cc75"},
                    "showSymbol": False
                }
            ]
        }
        return self._shortcode(
            "benford-law", option,
            title="🌰 Benford Law Test Score",
            caption="Scores above the critical value (dashed line) indicate anomalies"
        )

    def _make_vvcorrelation(self, data: list[dict]) -> str:
        """
        Volume-Volatility correlation over time — ECharts line chart with markers.
        🌰 Uses visualMap for colour gradient (high correlation = red).
        """
        timestamps = self._timestamps(data)
        values = [row.get("vvcorrelation") for row in data]

        numeric_values = [v for v in values if v is not None]
        if not numeric_values:
            return ""

        min_val = min(numeric_values)
        max_val = max(numeric_values)

        option = {
            "xAxis": {
                "type": "category",
                "data": timestamps,
                "axisLabel": {"rotate": 30}
            },
            "yAxis": {"type": "value", "name": "VV Correlation", "min": min_val - 0.05},
            "visualMap": {
                "show": False,
                "type": "continuous",
                "seriesIndex": 0,
                "min": min_val,
                "max": max_val,
                "inRange": {"color": ["#91cc75", "#fac858", "#ee6666"]}
            },
            "series": [{
                "name": "VV Correlation",
                "type": "line",
                "data": values,
                "showSymbol": True,
                "symbolSize": 4,
                "smooth": True
            }]
        }
        return self._shortcode(
            "vv-correlation", option,
            title="🌰 Volume-Volatility Correlation Over Time",
            caption="Gradient: green (low) → red (high correlation)"
        )

    def generate_report(self, data: list[dict], directory: str) -> str:
        """
        Generate all charts and append them to ``{directory}/index.md``.

        Parameters
        ----------
        data      : list of dicts with market data rows (timestamp, volume, etc.)
        directory : path to the article directory (must contain index.md)

        Returns
        -------
        Combined shortcode markdown string (all charts concatenated).
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        blocks = [
            self._make_volume_hist(data),
            self._make_crypto_metrics(data),
            self._make_benfordlaw(data),
            self._make_vvcorrelation(data),
        ]

        charts_md = "\n".join(b for b in blocks if b)

        index_path = os.path.join(directory, "index.md")
        if os.path.exists(index_path):
            with open(index_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + charts_md)

        return charts_md
