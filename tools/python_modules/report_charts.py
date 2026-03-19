"""
Generate Hugo shortcode chart snippets for market health reports.
Replaces static matplotlib PNG generation with dynamic Chart.js charts.
"""

import json
import os
import numpy as np
import pandas as pd


def _format_labels(timestamps: list) -> str:
    """Format timestamps as JSON array for Chart.js labels."""
    formatted = [t.strftime('%Y-%m-%d %H:%M') if hasattr(t, 'strftime') else str(t) for t in timestamps]
    return json.dumps(formatted)


def _format_data(values) -> str:
    """Format numeric series as JSON array, handling NaN."""
    cleaned = [round(float(v), 4) if not (np.isnan(v) if isinstance(v, float) else False) else 0 for v in values]
    return json.dumps(cleaned)


def generate_volume_hist_shortcode(data: pd.DataFrame) -> str:
    """Generate volume distribution histogram shortcode."""
    volumes = data['volume'].dropna()
    hist, bin_edges = np.histogram(volumes, bins=30)
    labels = [f"{bin_edges[i]:.0f}-{bin_edges[i+1]:.0f}" for i in range(len(hist))]

    return (
        f'{{{{% metric_chart id="volume-hist" type="bar" '
        f'title="Transaction Volume Distribution" '
        f'xlabel="Volume Range" ylabel="Frequency" '
        f'color="rgb(56, 189, 248)" '
        f'labels="{json.dumps(labels)}" '
        f'data="{json.dumps(hist.tolist())}" '
        f'caption="Distribution of transaction volumes across the analysis period" %}}}}'
    )


def generate_crypto_metrics_shortcode(data: pd.DataFrame) -> str:
    """Generate multi-metric time series shortcode."""
    labels = _format_labels(data.index.tolist())
    volume_data = _format_data(data['volume'])
    bsr_data = _format_data(data['buysellratio'])

    return (
        f'{{{{% metric_chart id="crypto-metrics" type="line" '
        f'title="Volume and Buy/Sell Ratio Over Time" '
        f'xlabel="Timestamp" ylabel="Volume" ylabel2="Buy/Sell Ratio" '
        f'color="rgb(59, 130, 246)" color2="rgb(239, 68, 68)" '
        f'labels=\'{labels}\' '
        f'data=\'{volume_data}\' '
        f'data2=\'{bsr_data}\' '
        f'caption="Trading volume (blue) and buy/sell ratio (red) over time" %}}}}'
    )


def generate_benford_shortcode(data: pd.DataFrame) -> str:
    """Generate Benford's Law test score chart shortcode."""
    labels = _format_labels(data.index.tolist())
    test_data = _format_data(data['benfordlawtest'])
    critical_data = _format_data(1.36 / np.sqrt(data['tradecount']))

    return (
        f'{{{{% metric_chart id="benford-law" type="line" '
        f'title="Benford Law K-S Test Score vs Critical Value" '
        f'xlabel="Timestamp" ylabel="Test Score" ylabel2="Critical Value" '
        f'color="rgb(59, 130, 246)" color2="rgb(34, 197, 94)" '
        f'labels=\'{labels}\' '
        f'data=\'{test_data}\' '
        f'data2=\'{critical_data}\' '
        f'caption="K-S test score (blue) vs critical value (green). Score above critical value indicates deviation from Benfords Law." %}}}}'
    )


def generate_vvcorrelation_shortcode(data: pd.DataFrame) -> str:
    """Generate volume-volatility correlation chart shortcode."""
    labels = _format_labels(data.index.tolist())
    corr_data = _format_data(data['vvcorrelation'])

    return (
        f'{{{{% metric_chart id="vv-correlation" type="line" '
        f'title="Volume-Volatility Correlation Over Time" '
        f'xlabel="Timestamp" ylabel="Correlation Coefficient" '
        f'color="rgb(168, 85, 247)" '
        f'labels=\'{labels}\' '
        f'data=\'{corr_data}\' '
        f'caption="Volume-volatility correlation. Values consistently below 0.4 suggest artificial trading volume." %}}}}'
    )


def generate_all_shortcodes(data: dict) -> dict:
    """Generate all chart shortcodes from raw API data.

    Returns dict mapping filename to shortcode string.
    """
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    return {
        'volume_hist': generate_volume_hist_shortcode(df),
        'crypto_metrics': generate_crypto_metrics_shortcode(df),
        'benford_law': generate_benford_shortcode(df),
        'vv_correlation': generate_vvcorrelation_shortcode(df),
    }


def save_shortcodes_to_file(shortcodes: dict, directory: str) -> None:
    """Save shortcodes to a reference file for manual inclusion."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, 'chart_shortcodes.md')
    with open(filepath, 'w') as f:
        f.write("<!-- Chart shortcodes for this report -->\n")
        f.write("<!-- Copy these into the article to replace static images -->\n\n")
        for name, shortcode in shortcodes.items():
            f.write(f"<!-- {name} -->\n")
            f.write(f"{shortcode}\n\n")
    print(f"Chart shortcodes saved to: {filepath}")
