"""
Market Health Reporter - Dynamic Chart Graphics Tool 🌰

Replaces static matplotlib PNG generation with interactive Apache ECharts charts
via Hugo shortcodes. Supports auto chart-type detection, data zoom, and export.

Chestnut overlords approved 🌰🌰🌰
"""

import json
import os
from datetime import datetime
from typing import Any


class Visualization:
    """Generate interactive ECharts charts via Hugo shortcodes 🌰"""
    
    def __init__(self):
        self.chart_counter = 0
    
    def _get_next_chart_id(self) -> str:
        """Generate unique chart ID 🌰"""
        self.chart_counter += 1
        return f"chart-{self.chart_counter}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _create_echarts_option(self, chart_type: str, title: str, data: dict, 
                               x_axis: list = None, y_axis: list = None,
                               series: list = None, **kwargs) -> dict:
        """
        Create Apache ECharts option object 🌰
        
        Supports: line, bar, scatter, candlestick, histogram
        Auto-enables: dataZoom, tooltip, legend, export
        """
        option = {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {
                    "fontSize": 16,
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "trigger": "axis" if chart_type in ["line", "bar"] else "item",
                "axisPointer": {
                    "type": "cross"
                },
                "extraCssText": "z-index: 9999;"
            },
            "legend": {
                "data": kwargs.get("legend_data", []),
                "bottom": "10",
                "type": "scroll"
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "containLabel": True
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {
                        "yAxisIndex": "none",
                        "title": {
                            "zoom": "🔍 Zoom",
                            "back": "↩️ Reset"
                        }
                    },
                    "brush": {
                        "type": ["rect", "polygon", "clear"],
                        "title": {
                            "rect": "📦 Box Select",
                            "polygon": "✏️ Lasso Select",
                            "clear": "🗑️ Clear"
                        }
                    },
                    "saveAsImage": {
                        "type": "png",
                        "title": "💾 Save PNG",
                        "pixelRatio": 2
                    }
                },
                "right": "10",
                "top": "10"
            },
            "dataZoom": [
                {
                    "type": "slider",
                    "show": True,
                    "xAxisIndex": [0],
                    "start": 0,
                    "end": 100,
                    "bottom": 30
                },
                {
                    "type": "inside",
                    "xAxisIndex": [0],
                    "start": 0,
                    "end": 100
                }
            ],
            "xAxis": x_axis,
            "yAxis": y_axis,
            "series": series
        }
        
        # Add responsive configuration 🌰
        option["responsive"] = True
        option["animation"] = True
        option["animationDuration"] = 1000
        
        return option
    
    def _generate_shortcode(self, chart_id: str, option: dict, 
                           height: str = "400px", caption: str = "") -> str:
        """
        Generate Hugo shortcode markdown 🌰
        
        Returns markdown block that will render ECharts chart
        """
        option_json = json.dumps(option, ensure_ascii=False, indent=2)
        
        shortcode = f"""{{{{< metric_chart_echarts
    id="{chart_id}"
    option='{option_json}'
    height="{height}"
    caption="{caption}"
>}}}}"""
        
        return shortcode
    
    def _make_volume_hist(self, data: dict, directory: str) -> str:
        """
        Volume histogram chart 🌰
        
        Replaces matplotlib histogram with interactive ECharts bar chart
        """
        chart_id = self._get_next_chart_id()
        
        # Prepare histogram data
        volumes = data.get('volume', [])
        bin_count = 30
        min_vol = min(volumes) if volumes else 0
        max_vol = max(volumes) if volumes else 100
        bin_width = (max_vol - min_vol) / bin_count
        
        # Calculate histogram bins
        bins = []
        counts = []
        for i in range(bin_count):
            bin_start = min_vol + i * bin_width
            bin_end = min_vol + (i + 1) * bin_width
            count = sum(1 for v in volumes if bin_start <= v < bin_end)
            bins.append(f"{bin_start:.2f}-{bin_end:.2f}")
            counts.append(count)
        
        option = self._create_echarts_option(
            chart_type="bar",
            title="🌰 Transaction Volume Distribution",
            data=data,
            x_axis={
                "type": "category",
                "data": bins,
                "name": "Volume Range",
                "axisLabel": {
                    "rotate": 45,
                    "interval": "auto"
                }
            },
            y_axis={
                "type": "value",
                "name": "Frequency",
                "splitLine": {
                    "lineStyle": {
                        "type": "dashed"
                    }
                }
            },
            series=[{
                "name": "Frequency",
                "type": "bar",
                "data": counts,
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "#5470c6"},
                            {"offset": 1, "color": "#91cc75"}
                        ]
                    },
                    "borderRadius": [4, 4, 0, 0]
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0,0,0,0.3)"
                    }
                }
            }],
            legend_data=["Frequency"]
        )
        
        shortcode = self._generate_shortcode(
            chart_id, option, height="400px",
            caption="Transaction volume distribution histogram (interactive) 🌰"
        )
        
        return shortcode
    
    def _make_crypto_metrics(self, data: dict, directory: str) -> str:
        """
        Multi-series crypto metrics chart 🌰
        
        Replaces 4 matplotlib subplots with single interactive multi-axis chart
        """
        chart_id = self._get_next_chart_id()
        
        # Extract time series data
        timestamps = data.get('timestamp', [])
        volume = data.get('volume', [])
        tradecount = data.get('tradecount', [])
        avg_tx_size = data.get('avgtransactionsize', [])
        buy_sell_ratio = data.get('buysellratio', [])
        
        option = self._create_echarts_option(
            chart_type="line",
            title="🌰 Cryptocurrency Metrics Over Time",
            data=data,
            x_axis={
                "type": "category",
                "data": timestamps,
                "name": "Timestamp",
                "axisLabel": {
                    "rotate": 45,
                    "interval": "auto"
                }
            },
            y_axis=[
                {
                    "type": "value",
                    "name": "Volume",
                    "position": "left",
                    "splitLine": {"lineStyle": {"type": "dashed"}}
                },
                {
                    "type": "value",
                    "name": "Trade Count",
                    "position": "right",
                    "splitLine": {"show": False}
                }
            ],
            series=[
                {
                    "name": "Volume",
                    "type": "line",
                    "data": volume,
                    "yAxisIndex": 0,
                    "smooth": True,
                    "areaStyle": {"opacity": 0.3},
                    "itemStyle": {"color": "#5470c6"}
                },
                {
                    "name": "Trade Count",
                    "type": "line",
                    "data": tradecount,
                    "yAxisIndex": 1,
                    "smooth": True,
                    "itemStyle": {"color": "#91cc75"}
                },
                {
                    "name": "Avg Transaction Size",
                    "type": "line",
                    "data": avg_tx_size,
                    "yAxisIndex": 0,
                    "smooth": True,
                    "itemStyle": {"color": "#fac858"}
                },
                {
                    "name": "Buy/Sell Ratio",
                    "type": "line",
                    "data": buy_sell_ratio,
                    "yAxisIndex": 1,
                    "smooth": True,
                    "markLine": {
                        "data": [{"yAxis": 1.0, "name": "Balance Line"}],
                        "lineStyle": {"color": "#ee6666", "type": "dashed"}
                    },
                    "itemStyle": {"color": "#ee6666"}
                }
            ],
            legend_data=["Volume", "Trade Count", "Avg Transaction Size", "Buy/Sell Ratio"]
        )
        
        shortcode = self._generate_shortcode(
            chart_id, option, height="500px",
            caption="Multi-axis crypto metrics comparison (zoom/pan enabled) 🌰"
        )
        
        return shortcode
    
    def _make_benfordlaw(self, data: dict, directory: str) -> str:
        """
        Benford Law test score vs critical value 🌰
        
        Dual-axis chart with threshold visualization
        """
        chart_id = self._get_next_chart_id()
        
        timestamps = data.get('timestamp', [])
        benford_scores = data.get('benfordlawtest', [])
        trade_counts = data.get('tradecount', [])
        
        # Calculate critical values: 1.36 / sqrt(n)
        critical_values = [1.36 / (n ** 0.5) if n > 0 else 0 for n in trade_counts]
        
        option = self._create_echarts_option(
            chart_type="line",
            title="🌰 Benford Law Test Score vs Critical Value",
            data=data,
            x_axis={
                "type": "category",
                "data": timestamps,
                "name": "Timestamp",
                "axisLabel": {"rotate": 45}
            },
            y_axis=[
                {
                    "type": "value",
                    "name": "Benford Test Score",
                    "position": "left",
                    "splitLine": {"lineStyle": {"type": "dashed"}}
                },
                {
                    "type": "value",
                    "name": "Trade Count",
                    "position": "right",
                    "splitLine": {"show": False}
                }
            ],
            series=[
                {
                    "name": "Benford Test Score",
                    "type": "line",
                    "data": benford_scores,
                    "yAxisIndex": 0,
                    "smooth": True,
                    "itemStyle": {"color": "#5470c6"},
                    "markLine": {
                        "symbol": "none",
                        "data": [{"type": "average", "name": "Average"}]
                    }
                },
                {
                    "name": "Critical Value (1.36/√n)",
                    "type": "line",
                    "data": critical_values,
                    "yAxisIndex": 0,
                    "smooth": True,
                    "lineStyle": {"type": "dashed"},
                    "itemStyle": {"color": "#91cc75"},
                    "areaStyle": {"opacity": 0.1}
                },
                {
                    "name": "Trade Count",
                    "type": "bar",
                    "data": trade_counts,
                    "yAxisIndex": 1,
                    "itemStyle": {"color": "#fac858", "opacity": 0.5}
                }
            ],
            legend_data=["Benford Test Score", "Critical Value (1.36/√n)", "Trade Count"]
        )
        
        shortcode = self._generate_shortcode(
            chart_id, option, height="450px",
            caption="Benford Law compliance test with critical value threshold 🌰"
        )
        
        return shortcode
    
    def _make_vvcorrelation(self, data: dict, directory: str) -> str:
        """
        Volume-Volatility Correlation over time 🌰
        
        Line chart with gradient fill and mark points for extremes
        """
        chart_id = self._get_next_chart_id()
        
        timestamps = data.get('timestamp', [])
        vv_corr = data.get('vvcorrelation', [])
        
        # Find min/max points for annotation
        if vv_corr:
            max_idx = vv_corr.index(max(vv_corr))
            min_idx = vv_corr.index(min(vv_corr))
            mark_point_data = [
                {"coord": [timestamps[max_idx], vv_corr[max_idx]], "name": "Max"},
                {"coord": [timestamps[min_idx], vv_corr[min_idx]], "name": "Min"}
            ]
        else:
            mark_point_data = []
        
        option = self._create_echarts_option(
            chart_type="line",
            title="🌰 Volume-Volatility Correlation Over Time",
            data=data,
            x_axis={
                "type": "category",
                "data": timestamps,
                "name": "Timestamp",
                "axisLabel": {"rotate": 45}
            },
            y_axis={
                "type": "value",
                "name": "VV Correlation",
                "splitLine": {"lineStyle": {"type": "dashed"}},
                "scale": True  # Don't force zero baseline for correlation
            },
            series=[{
                "name": "VV Correlation",
                "type": "line",
                "data": vv_corr,
                "smooth": True,
                "areaStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(145,204,117,0.8)"},
                            {"offset": 1, "color": "rgba(145,204,117,0.1)"}
                        ]
                    }
                },
                "itemStyle": {"color": "#91cc75"},
                "markPoint": {
                    "data": mark_point_data,
                    "symbol": "pin",
                    "symbolSize": 50
                },
                "markLine": {
                    "data": [
                        {"yAxis": 0, "name": "Zero Line", "lineStyle": {"color": "#ee6666"}}
                    ]
                }
            }],
            legend_data=["VV Correlation"]
        )
        
        shortcode = self._generate_shortcode(
            chart_id, option, height="400px",
            caption="Volume-volatility correlation with extreme point markers 🌰"
        )
        
        return shortcode
    
    def generate_report(self, data: list, directory: str) -> str:
        """
        Generate complete report with all interactive charts 🌰
        
        Returns markdown string with all chart shortcodes embedded.
        The calling code should inject this into the article .md file.
        
        Args:
            data: List of dicts with market health metrics
            directory: Output directory (kept for API compatibility)
        
        Returns:
            Markdown string containing all chart shortcodes 🌰
        """
        import pandas as pd
        
        # Reset chart counter for fresh report
        self.chart_counter = 0
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Convert to dict for chart generation
        data_dict = {
            'timestamp': [ts.strftime('%Y-%m-%d %H:%M') for ts in df.index.tolist()],
            'volume': df['volume'].tolist(),
            'tradecount': df['tradecount'].tolist(),
            'avgtransactionsize': df['avgtransactionsize'].tolist(),
            'buysellratio': df['buysellratio'].tolist(),
            'benfordlawtest': df['benfordlawtest'].tolist(),
            'vvcorrelation': df['vvcorrelation'].tolist()
        }
        
        # Generate all charts 🌰🌰🌰
        charts = []
        
        charts.append("## 🌰 Interactive Charts\n")
        charts.append("*All charts support zoom, pan, and export. Click legend to toggle series.*\n")
        
        charts.append("### Volume Distribution\n")
        charts.append(self._make_volume_hist(data_dict, directory))
        charts.append("\n")
        
        charts.append("### Crypto Metrics Overview\n")
        charts.append(self._make_crypto_metrics(data_dict, directory))
        charts.append("\n")
        
        charts.append("### Benford Law Compliance\n")
        charts.append(self._make_benfordlaw(data_dict, directory))
        charts.append("\n")
        
        charts.append("### Volume-Volatility Correlation\n")
        charts.append(self._make_vvcorrelation(data_dict, directory))
        charts.append("\n")
        
        # Add chart usage instructions 🌰
        charts.append("---\n")
        charts.append("### 🌰 Chart Features\n")
        charts.append("- 🔍 **Data Zoom**: Use slider or mouse wheel to zoom\n")
        charts.append("- 📦 **Brush Select**: Click box/lasso tool to select regions\n")
        charts.append("- 💾 **Export**: Click save button to download PNG\n")
        charts.append("- 📱 **Responsive**: Auto-scales for mobile/desktop\n")
        charts.append("- 🌰 **Chestnut Approved**: All charts blessed by overlords\n")
        
        return "\n".join(charts)
