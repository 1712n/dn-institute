import openai
import json
import os
import math
import re
from datetime import datetime
from tools.python_modules.utils import read_file


CHART_SYSTEM_PROMPT_FILE = 'tools/chart_generator/doc/prompts/system_prompt.txt'
CHART_CONFIG_PROMPT_FILE = 'tools/chart_generator/doc/prompts/chart_config_prompt.txt'

# Default color palette for charts
COLORS = {
    'blue': 'rgb(54, 162, 235)',
    'red': 'rgb(255, 99, 132)',
    'green': 'rgb(75, 192, 192)',
    'orange': 'rgb(255, 159, 64)',
    'purple': 'rgb(153, 102, 255)',
    'yellow': 'rgb(255, 205, 86)',
    'grey': 'rgb(201, 203, 207)',
    'teal': 'rgb(0, 128, 128)',
    'pink': 'rgb(255, 105, 180)',
    'dark_blue': 'rgb(0, 0, 139)',
}


def format_timestamp(ts):
    """Format a timestamp string into a readable date label."""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %H:%M')
    except (ValueError, AttributeError):
        return str(ts)


def build_volume_distribution_chart(data):
    """Build a Chart.js config for the volume distribution histogram."""
    volume_bins = [0] * 100
    for record in data:
        if 'volumedist' in record and record['volumedist']:
            for i, bin_data in enumerate(record['volumedist']):
                if i < 100:
                    volume_bins[i] += bin_data[1] if isinstance(bin_data, list) else 0

    last_nonzero = 0
    for i in range(len(volume_bins) - 1, -1, -1):
        if volume_bins[i] > 0:
            last_nonzero = i
            break
    display_bins = volume_bins[:last_nonzero + 1] if last_nonzero > 0 else volume_bins

    return {
        "id": "volume-distribution",
        "caption": "Trading volume distribution aggregated over the analysis period",
        "height": "400px",
        "config": {
            "type": "bar",
            "data": {
                "labels": list(range(len(display_bins))),
                "datasets": [{
                    "label": "Volume Distribution (Aggregated)",
                    "data": display_bins,
                    "backgroundColor": COLORS['blue'],
                    "borderColor": COLORS['dark_blue'],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Trading Volume Distribution",
                        "font": {"size": 16}
                    },
                    "legend": {"display": True}
                },
                "scales": {
                    "x": {"title": {"display": True, "text": "Volume Bin"}},
                    "y": {"title": {"display": True, "text": "Frequency"}, "beginAtZero": True}
                }
            }
        }
    }


def build_crypto_metrics_chart(data):
    """Build a Chart.js config for multi-metric time series."""
    timestamps = [format_timestamp(r['timestamp']) for r in data]
    volumes = [r.get('volume', 0) for r in data]
    trade_counts = [r.get('tradecount', 0) for r in data]
    avg_tx_sizes = [r.get('avgtransactionsize', 0) for r in data]
    buy_sell_ratios = [r.get('buysellratio', 0) for r in data]

    return {
        "id": "crypto-metrics",
        "caption": "Key cryptocurrency trading metrics over time: volume, trade count, average transaction size, and buy/sell ratio",
        "height": "500px",
        "config": {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Volume",
                        "data": volumes,
                        "borderColor": COLORS['blue'],
                        "backgroundColor": "rgba(54, 162, 235, 0.1)",
                        "borderWidth": 2, "tension": 0.1, "pointRadius": 0,
                        "yAxisID": "y"
                    },
                    {
                        "label": "Trade Count",
                        "data": trade_counts,
                        "borderColor": COLORS['green'],
                        "backgroundColor": "rgba(75, 192, 192, 0.1)",
                        "borderWidth": 2, "tension": 0.1, "pointRadius": 0,
                        "yAxisID": "y1"
                    },
                    {
                        "label": "Avg Transaction Size",
                        "data": avg_tx_sizes,
                        "borderColor": COLORS['orange'],
                        "backgroundColor": "rgba(255, 159, 64, 0.1)",
                        "borderWidth": 2, "tension": 0.1, "pointRadius": 0,
                        "yAxisID": "y2"
                    },
                    {
                        "label": "Buy/Sell Ratio",
                        "data": buy_sell_ratios,
                        "borderColor": COLORS['red'],
                        "backgroundColor": "rgba(255, 99, 132, 0.1)",
                        "borderWidth": 2, "tension": 0.1, "pointRadius": 0,
                        "yAxisID": "y3"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {"display": True, "text": "Cryptocurrency Trading Metrics Over Time", "font": {"size": 16}},
                    "legend": {"display": True, "position": "top"}
                },
                "scales": {
                    "x": {"ticks": {"maxTicksLimit": 12, "maxRotation": 45}},
                    "y": {"type": "linear", "display": True, "position": "left", "title": {"display": True, "text": "Volume"}},
                    "y1": {"type": "linear", "display": False, "position": "right", "grid": {"drawOnChartArea": False}},
                    "y2": {"type": "linear", "display": False, "position": "right", "grid": {"drawOnChartArea": False}},
                    "y3": {"type": "linear", "display": True, "position": "right", "title": {"display": True, "text": "Buy/Sell Ratio"}, "grid": {"drawOnChartArea": False}, "min": 0, "max": 1}
                }
            }
        }
    }


def build_benford_law_chart(data):
    """Build a Chart.js config for Benford's Law analysis over time."""
    timestamps = [format_timestamp(r['timestamp']) for r in data]
    benford_scores = [r.get('benfordlawtest', 0) for r in data]
    trade_counts = [r.get('tradecount', 0) for r in data]
    critical_values = [1.36 / math.sqrt(tc) if tc > 0 else 0 for tc in trade_counts]

    return {
        "id": "benford-law",
        "caption": "Benford's Law K-S test score vs. critical value over time. When the test score exceeds the critical value, the data deviates from Benford's Law.",
        "height": "400px",
        "config": {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "K-S Test Score",
                        "data": benford_scores,
                        "borderColor": COLORS['blue'],
                        "backgroundColor": "rgba(54, 162, 235, 0.1)",
                        "borderWidth": 2, "tension": 0.1, "pointRadius": 0, "fill": False
                    },
                    {
                        "label": "Critical Value (1.36/sqrt(n))",
                        "data": critical_values,
                        "borderColor": COLORS['red'],
                        "backgroundColor": "rgba(255, 99, 132, 0.1)",
                        "borderWidth": 2, "borderDash": [5, 5],
                        "tension": 0.1, "pointRadius": 0, "fill": False
                    }
                ]
            },
            "options": {
                "responsive": True, "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": True, "text": "Benford's Law Test Score vs Critical Value", "font": {"size": 16}},
                    "legend": {"display": True, "position": "top"}
                },
                "scales": {
                    "x": {"ticks": {"maxTicksLimit": 12, "maxRotation": 45}},
                    "y": {"title": {"display": True, "text": "Test Statistic"}, "beginAtZero": True}
                }
            }
        }
    }


def build_vv_correlation_chart(data):
    """Build a Chart.js config for volume-volatility correlation over time."""
    timestamps = [format_timestamp(r['timestamp']) for r in data]
    vv_corr = [r.get('vvcorrelation', 0) for r in data]
    threshold_line = [0.4] * len(timestamps)

    return {
        "id": "vv-correlation",
        "caption": "Volume-Volatility correlation over time. Values consistently below 0.4 may indicate artificial trading volume.",
        "height": "400px",
        "config": {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "VV Correlation",
                        "data": vv_corr,
                        "borderColor": COLORS['purple'],
                        "backgroundColor": "rgba(153, 102, 255, 0.1)",
                        "borderWidth": 2, "tension": 0.1, "pointRadius": 2,
                        "pointBackgroundColor": COLORS['purple'], "fill": False
                    },
                    {
                        "label": "Suspicion Threshold (0.4)",
                        "data": threshold_line,
                        "borderColor": COLORS['red'],
                        "borderWidth": 2, "borderDash": [10, 5],
                        "pointRadius": 0, "fill": False
                    }
                ]
            },
            "options": {
                "responsive": True, "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": True, "text": "Volume-Volatility Correlation Over Time", "font": {"size": 16}},
                    "legend": {"display": True, "position": "top"}
                },
                "scales": {
                    "x": {"ticks": {"maxTicksLimit": 12, "maxRotation": 45}},
                    "y": {"title": {"display": True, "text": "Correlation Coefficient"}, "min": -1, "max": 1}
                }
            }
        }
    }


def build_buy_sell_ratio_chart(data):
    """Build a Chart.js config for buy/sell ratio over time."""
    timestamps = [format_timestamp(r['timestamp']) for r in data]
    ratios = [r.get('buysellratio', 0) for r in data]
    ratios_abs = [r.get('buysellratioabs', 0) for r in data]

    return {
        "id": "buy-sell-ratio",
        "caption": "Buy/sell ratio over time. The shaded region (0.4-0.6) represents the normal range for a balanced market.",
        "height": "400px",
        "config": {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Upper Normal Bound (0.6)",
                        "data": [0.6] * len(timestamps),
                        "borderColor": "rgba(75, 192, 192, 0.3)",
                        "backgroundColor": "rgba(75, 192, 192, 0.1)",
                        "borderWidth": 1, "borderDash": [5, 5],
                        "pointRadius": 0, "fill": "+1"
                    },
                    {
                        "label": "Lower Normal Bound (0.4)",
                        "data": [0.4] * len(timestamps),
                        "borderColor": "rgba(75, 192, 192, 0.3)",
                        "backgroundColor": "rgba(75, 192, 192, 0.1)",
                        "borderWidth": 1, "borderDash": [5, 5],
                        "pointRadius": 0, "fill": False
                    },
                    {
                        "label": "Buy/Sell Ratio",
                        "data": ratios,
                        "borderColor": COLORS['green'],
                        "borderWidth": 2, "tension": 0.1,
                        "pointRadius": 0, "fill": False
                    },
                    {
                        "label": "Buy/Sell Ratio (Absolute)",
                        "data": ratios_abs,
                        "borderColor": COLORS['blue'],
                        "borderWidth": 2, "tension": 0.1,
                        "pointRadius": 0, "fill": False
                    }
                ]
            },
            "options": {
                "responsive": True, "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": True, "text": "Buy/Sell Ratio Over Time", "font": {"size": 16}},
                    "legend": {"display": True, "position": "top"},
                    "filler": {"propagate": True}
                },
                "scales": {
                    "x": {"ticks": {"maxTicksLimit": 12, "maxRotation": 45}},
                    "y": {"title": {"display": True, "text": "Ratio"}, "min": 0, "max": 1}
                }
            }
        }
    }


def build_first_digit_distribution_chart(data):
    """Build a Chart.js config for first digit distribution vs Benford's Law."""
    fdd_data = [0] * 9
    for record in data:
        if 'firstdigitdist' in record and record['firstdigitdist']:
            fdd = record['firstdigitdist']
            for j in range(9):
                key = str(j + 1)
                fdd_data[j] += fdd.get(key, 0) if isinstance(fdd, dict) else 0

    total_fdd = sum(fdd_data)
    benford_pcts = [301, 176, 125, 97, 79, 67, 58, 51, 46]
    expected_fdd = [(total_fdd * p) / 1000 for p in benford_pcts]

    return {
        "id": "first-digit-distribution",
        "caption": "Observed first digit distribution compared to Benford's Law expected distribution. Significant deviations may indicate data manipulation.",
        "height": "400px",
        "config": {
            "type": "bar",
            "data": {
                "labels": [str(i) for i in range(1, 10)],
                "datasets": [
                    {
                        "label": "Observed Distribution",
                        "data": fdd_data,
                        "backgroundColor": COLORS['orange'],
                        "borderColor": "rgba(255, 159, 64, 0.8)",
                        "borderWidth": 1
                    },
                    {
                        "label": "Expected (Benford's Law)",
                        "data": expected_fdd,
                        "backgroundColor": COLORS['blue'],
                        "borderColor": "rgba(54, 162, 235, 0.8)",
                        "borderWidth": 1
                    }
                ]
            },
            "options": {
                "responsive": True, "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": True, "text": "First Digit Distribution vs Benford's Law", "font": {"size": 16}},
                    "legend": {"display": True, "position": "top"}
                },
                "scales": {
                    "x": {"title": {"display": True, "text": "Leading Digit"}},
                    "y": {"title": {"display": True, "text": "Frequency"}, "beginAtZero": True}
                }
            }
        }
    }


def build_time_of_trade_chart(data):
    """Build a Chart.js config for time-of-trade distribution."""
    seconds_data = [0] * 60
    total_trades = 0
    for record in data:
        if 'timeoftrade' in record and record['timeoftrade']:
            tot = record['timeoftrade']
            seconds = tot.get('seconds', [])
            for i, count in enumerate(seconds):
                if i < 60:
                    seconds_data[i] += count
                    total_trades += count

    avg_trades = total_trades / 60 if total_trades > 0 else 0
    avg_line = [avg_trades] * 60

    return {
        "id": "time-of-trade",
        "caption": "Trade frequency by second within each minute, aggregated over the analysis period. Uniform distribution or sharp spikes may indicate bot activity.",
        "height": "400px",
        "config": {
            "type": "bar",
            "data": {
                "labels": list(range(60)),
                "datasets": [
                    {
                        "label": "Trade Count per Second",
                        "data": seconds_data,
                        "backgroundColor": COLORS['green'],
                        "borderColor": "rgba(75, 192, 192, 0.8)",
                        "borderWidth": 1, "type": "bar"
                    },
                    {
                        "label": "Average",
                        "data": avg_line,
                        "borderColor": COLORS['red'],
                        "borderWidth": 2, "borderDash": [5, 5],
                        "pointRadius": 0, "type": "line", "fill": False
                    }
                ]
            },
            "options": {
                "responsive": True, "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": True, "text": "Time-of-Trade Distribution (Per Second)", "font": {"size": 16}},
                    "legend": {"display": True, "position": "top"}
                },
                "scales": {
                    "x": {"title": {"display": True, "text": "Second within Minute"}},
                    "y": {"title": {"display": True, "text": "Trade Count"}, "beginAtZero": True}
                }
            }
        }
    }


# Registry of all available chart builders
CHART_BUILDERS = {
    'volume_distribution': build_volume_distribution_chart,
    'crypto_metrics': build_crypto_metrics_chart,
    'benford_law': build_benford_law_chart,
    'vv_correlation': build_vv_correlation_chart,
    'buy_sell_ratio': build_buy_sell_ratio_chart,
    'first_digit_distribution': build_first_digit_distribution_chart,
    'time_of_trade': build_time_of_trade_chart,
}

# Mapping from old static image names to chart builder keys
STATIC_IMAGE_TO_CHART = {
    'volume_hist.png': 'volume_distribution',
    'crypto_metrics.png': 'crypto_metrics',
    'benford_law.png': 'benford_law',
    'vv_correlation.png': 'vv_correlation',
}


def generate_all_charts(data):
    """Generate all chart configurations from the market data."""
    charts = []
    for name, builder in CHART_BUILDERS.items():
        try:
            chart = builder(data)
            charts.append(chart)
        except Exception as e:
            print(f"Warning: Failed to generate chart '{name}': {e}")
    return charts


def select_charts_with_llm(data, api_key, model="gpt-4-0125-preview"):
    """Use an LLM to analyze data and determine which charts to generate and
    in what order, based on detected anomalies."""
    system_prompt = read_file(CHART_SYSTEM_PROMPT_FILE)
    config_prompt = read_file(CHART_CONFIG_PROMPT_FILE)

    summary = _build_data_summary(data)

    user_prompt = (
        f"{config_prompt}\n\n"
        f"<data_summary>\n{json.dumps(summary, indent=2)}\n</data_summary>\n\n"
        f"Based on this data summary, return a JSON object with two keys:\n"
        f'1. "chart_order": An array of chart type keys from this list, ordered by importance for this specific data:\n'
        f"   {json.dumps(list(CHART_BUILDERS.keys()))}\n"
        f'2. "reasoning": A brief explanation of why you chose this ordering.\n\n'
        f"Return ONLY valid JSON, no other text."
    )

    openai.api_key = api_key
    completion = openai.ChatCompletion.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    response_text = completion.choices[0].message.content.strip()

    try:
        result = json.loads(response_text)
        chart_order = result.get("chart_order", list(CHART_BUILDERS.keys()))
        reasoning = result.get("reasoning", "")
        chart_order = [c for c in chart_order if c in CHART_BUILDERS]
        return chart_order, reasoning
    except json.JSONDecodeError:
        print("Warning: LLM returned invalid JSON for chart selection. Using default order.")
        return list(CHART_BUILDERS.keys()), ""


def _build_data_summary(data):
    """Build a compact summary of the data for LLM analysis."""
    if not data:
        return {}

    n = len(data)
    summary = {
        "record_count": n,
        "time_range": {
            "start": data[0].get('timestamp', 'unknown'),
            "end": data[-1].get('timestamp', 'unknown')
        },
        "metrics": {}
    }

    numeric_keys = [
        'volume', 'tradecount', 'avgtransactionsize',
        'buysellratio', 'buysellratioabs', 'vwap',
        'vvcorrelation', 'benfordlawtest'
    ]

    for key in numeric_keys:
        values = [r.get(key, 0) for r in data if r.get(key) is not None]
        if values:
            summary["metrics"][key] = {
                "min": round(min(values), 6),
                "max": round(max(values), 6),
                "mean": round(sum(values) / len(values), 6),
                "first_5": [round(v, 6) for v in values[:5]],
                "last_5": [round(v, 6) for v in values[-5:]]
            }

    benford_exceeds = 0
    for r in data:
        tc = r.get('tradecount', 0)
        bt = r.get('benfordlawtest', 0)
        if tc > 0 and bt > 1.36 / math.sqrt(tc):
            benford_exceeds += 1
    summary["benford_violations"] = benford_exceeds
    summary["benford_violation_rate"] = round(benford_exceeds / n, 4) if n > 0 else 0

    vv_below = sum(1 for r in data if r.get('vvcorrelation', 1) < 0.4)
    summary["vv_below_threshold"] = vv_below
    summary["vv_below_threshold_rate"] = round(vv_below / n, 4) if n > 0 else 0

    bsr_abnormal = sum(
        1 for r in data
        if r.get('buysellratio', 0.5) < 0.4 or r.get('buysellratio', 0.5) > 0.6
    )
    summary["bsr_abnormal_count"] = bsr_abnormal
    summary["bsr_abnormal_rate"] = round(bsr_abnormal / n, 4) if n > 0 else 0

    return summary


def generate_charts_for_report(data, api_key=None, model="gpt-4-0125-preview"):
    """Generate chart configurations for a market health report.

    If an API key is provided, uses the LLM to determine chart ordering
    based on data analysis. Otherwise, generates all charts in default order.
    """
    reasoning = ""

    if api_key:
        try:
            chart_order, reasoning = select_charts_with_llm(data, api_key, model)
            print(f"LLM chart ordering: {chart_order}")
            if reasoning:
                print(f"LLM reasoning: {reasoning}")
        except Exception as e:
            print(f"Warning: LLM chart selection failed ({e}). Using default order.")
            chart_order = list(CHART_BUILDERS.keys())
    else:
        chart_order = list(CHART_BUILDERS.keys())

    charts = []
    for chart_type in chart_order:
        builder = CHART_BUILDERS.get(chart_type)
        if builder:
            try:
                chart = builder(data)
                charts.append(chart)
            except Exception as e:
                print(f"Warning: Failed to generate chart '{chart_type}': {e}")

    return charts, reasoning


def charts_to_shortcodes(charts):
    """Convert chart configurations to Hugo dynamic_chart shortcode strings."""
    shortcodes = []
    for chart in charts:
        chart_id = chart['id']
        caption = chart.get('caption', '')
        height = chart.get('height', '400px')
        config_json = json.dumps(chart['config'])

        shortcode = (
            '{{< dynamic_chart id="' + chart_id + '" '
            'height="' + height + '" '
            'caption="' + caption + '" >}}\n'
            + config_json + '\n'
            '{{< /dynamic_chart >}}'
        )
        shortcodes.append(shortcode)
    return shortcodes


def replace_static_images_in_markdown(markdown_content, charts):
    """Replace static figure shortcodes with dynamic chart shortcodes in markdown."""
    chart_by_id = {c['id']: c for c in charts}

    for static_name, chart_key in STATIC_IMAGE_TO_CHART.items():
        chart_id_mapping = {
            'volume_distribution': 'volume-distribution',
            'crypto_metrics': 'crypto-metrics',
            'benford_law': 'benford-law',
            'vv_correlation': 'vv-correlation',
        }
        chart_id = chart_id_mapping.get(chart_key, chart_key)
        chart = chart_by_id.get(chart_id)

        if chart:
            pattern = (
                r'\{\{<\s*figure\s+[^>]*src\s*=\s*"'
                + re.escape(static_name)
                + r'"[^>]*>\}\}'
            )
            shortcode_list = charts_to_shortcodes([chart])
            if shortcode_list:
                markdown_content = re.sub(pattern, shortcode_list[0], markdown_content)

    return markdown_content
