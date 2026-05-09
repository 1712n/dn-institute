"""
Dynamic chart generation for Market Health Reporter.

Replaces static matplotlib PNG images with interactive Plotly charts
rendered via Hugo shortcodes. Generates JSON data files and Hugo
shortcode markup that can be embedded in markdown articles.

🌰🌰🌰
"""

import json
import os
from typing import Optional


class DynamicVisualization:
    """
    Generates Hugo shortcode markup for interactive Plotly charts
    from market health data.
    """

    def __init__(self, chart_height: int = 450):
        self.chart_height = chart_height

    def _make_volume_hist_shortcode(self, data: dict) -> str:
        """
        Generate shortcode for transaction volume distribution histogram.
        Uses Plotly histogram type for automatic binning.
        """
        volumes = data.get("volume", [])
        if not volumes:
            return ""

        values_json = json.dumps(volumes)
        return (
            f'{{{{< market_chart id="volume-hist" type="histogram" '
            f'title="Transaction Volume Distribution" '
            f'xLabel="Transaction Volume" yLabel="Frequency" '
            f'height="{self.chart_height}" >}}}}\n'
            f'{{"values": {values_json}}}\n'
            f'{{{{< /market_chart >}}}}'
        )

    def _make_crypto_metrics_shortcode(self, data: dict) -> str:
        """
        Generate shortcode for crypto metrics time series (4-panel).
        Uses multi-series line chart with datasets format.
        """
        timestamps = data.get("timestamp", [])
        if not timestamps:
            return ""

        # Format timestamps for display
        labels = [t.replace("T", " ")[:16] for t in timestamps]

        datasets = []
        metric_keys = [
            ("volume", "Volume"),
            ("tradecount", "Trade Count"),
            ("avgtransactionsize", "Avg Transaction Size"),
            ("buysellratio", "Buy/Sell Ratio"),
        ]

        for key, label in metric_keys:
            values = data.get(key, [])
            if values:
                datasets.append({"label": label, "data": values})

        if not datasets:
            return ""

        chart_data = json.dumps({"labels": labels, "datasets": datasets})
        return (
            f'{{{{< market_chart id="crypto-metrics" type="line" '
            f'title="Cryptocurrency Metrics Over Time" '
            f'xLabel="Timestamp" yLabel="Value" '
            f'height="{self.chart_height + 100}" >}}}}\n'
            f'{chart_data}\n'
            f'{{{{< /market_chart >}}}}'
        )

    def _make_benford_law_shortcode(self, data: dict) -> str:
        """
        Generate shortcode for Benford's Law test score with critical value.
        Uses dual-axis line chart.
        """
        import numpy as np

        timestamps = data.get("timestamp", [])
        benford_scores = data.get("benfordlawtest", [])
        trade_counts = data.get("tradecount", [])

        if not timestamps or not benford_scores or not trade_counts:
            return ""

        labels = [t.replace("T", " ")[:16] for t in timestamps]

        # Calculate critical values
        tc = np.array(trade_counts, dtype=float)
        critical_values = [1.36 / np.sqrt(x) if x > 0 else 0 for x in tc]

        chart_data = json.dumps({
            "x": labels,
            "y1": benford_scores,
            "y2": critical_values,
            "y1Label": "Benford Law Test Score",
            "y2Label": "Critical Value (1.36/√n)",
        })
        return (
            f'{{{{< market_chart id="benford-law" type="dual-line" '
            f'title="Benford Law Test Score vs Critical Value" '
            f'xLabel="Timestamp" yLabel="Test Score" '
            f'y2axis="true" y2Label="Critical Value" '
            f'height="{self.chart_height}" >}}}}\n'
            f'{chart_data}\n'
            f'{{{{< /market_chart >}}}}'
        )

    def _make_vv_correlation_shortcode(self, data: dict) -> str:
        """
        Generate shortcode for Volume-Volatility correlation over time.
        Uses single line chart with threshold reference.
        """
        timestamps = data.get("timestamp", [])
        vv_corr = data.get("vvcorrelation", [])

        if not timestamps or not vv_corr:
            return ""

        labels = [t.replace("T", " ")[:16] for t in timestamps]

        chart_data = json.dumps({
            "x": labels,
            "y": vv_corr,
        })
        return (
            f'{{{{< market_chart id="vv-correlation" type="line" '
            f'title="Volume-Volatility Correlation Over Time" '
            f'xLabel="Timestamp" yLabel="Correlation Coefficient" '
            f'height="{self.chart_height}" >}}}}\n'
            f'{chart_data}\n'
            f'{{{{< /market_chart >}}}}'
        )

    def generate_report(
        self,
        data: dict,
        directory: str,
        embed_in_article: Optional[str] = None,
    ) -> str:
        """
        Generate interactive chart shortcodes for the market health report.

        Args:
            data: Market data dict with keys like 'volume', 'timestamp', etc.
            directory: Output directory for chart data files
            embed_in_article: If provided, insert chart shortcodes into the
                article markdown at appropriate locations

        Returns:
            Combined shortcode markup string
        """
        os.makedirs(directory, exist_ok=True)

        shortcodes = []

        # Generate each chart shortcode
        charts = [
            ("volume_hist", self._make_volume_hist_shortcode),
            ("crypto_metrics", self._make_crypto_metrics_shortcode),
            ("benford_law", self._make_benford_law_shortcode),
            ("vv_correlation", self._make_vv_correlation_shortcode),
        ]

        for name, generator in charts:
            try:
                shortcode = generator(data)
                if shortcode:
                    shortcodes.append(shortcode)
                    # Also save the raw data as JSON for external use
                    self._save_chart_data(data, directory, name)
            except Exception as e:
                print(f"Warning: Failed to generate {name} chart: {e}")

        result = "\n\n".join(shortcodes)

        # Save combined shortcodes to a file
        shortcode_path = os.path.join(directory, "charts.md")
        with open(shortcode_path, "w", encoding="utf-8") as f:
            f.write(result)

        print(f"Generated {len(shortcodes)} interactive chart shortcodes")
        return result

    def _save_chart_data(self, data: dict, directory: str, chart_name: str):
        """Save chart data as JSON for external consumption."""
        # Extract relevant keys for each chart type
        chart_data = {}
        for key in data:
            if isinstance(data[key], (list, dict)):
                chart_data[key] = data[key]

        json_path = os.path.join(directory, f"{chart_name}_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(chart_data, f, indent=2, default=str)


def replace_figure_shortcodes(article: str, directory: str) -> str:
    """
    Replace static figure shortcodes in the article with interactive
    chart shortcodes where appropriate.

    Maps:
      volume_hist.png     → volume-hist histogram
      crypto_metrics.png  → crypto-metrics multi-line
      benford_law.png     → benford-law dual-axis
      vv_correlation.png  → vv-correlation line
    """
    import re

    # Mapping of static image filenames to chart IDs and types
    replacements = {
        'volume_hist.png': ('volume-hist', 'histogram'),
        'crypto_metrics.png': ('crypto-metrics', 'line'),
        'benford_law.png': ('benford-law', 'dual-line'),
        'vv_correlation.png': ('vv-correlation', 'line'),
    }

    for filename, (chart_id, chart_type) in replacements.items():
        # Match Hugo figure shortcodes referencing this image
        pattern = (
            r'\{\{<\s*figure\s+src="' + re.escape(filename) + r'"\s*'
            r'(?:alt="[^"]*"\s*)?'
            r'(?:caption="([^"]*)"\s*)?'
            r'(?:loading="[^"]*"\s*)?'
            r'>\}\}'
        )

        def make_shortcode(match, cid=chart_id, ct=chart_type):
            caption = match.group(1) or ""
            return (
                f'{{{{< market_chart id="{cid}" type="{ct}" '
                f'title="{caption}" >}}}}\n'
                f'{{{{< /market_chart >}}}}'
            )

        article = re.sub(pattern, make_shortcode, article)

    return article
