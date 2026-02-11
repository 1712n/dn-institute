"""
Report Graphics Tool - Generates Chart.js JSON configurations for market health reports.

Replaces the previous matplotlib PNG generation with dynamic, client-side Chart.js
rendering. Supports optional LLM-generated annotations for highlighting anomalies.

Charts are rendered via the {{< dynamic_chart >}} Hugo shortcode.
"""

import json
import os
import pandas as pd
import numpy as np


class Visualization:
    """Generates Chart.js configuration JSON files for market health report charts."""

    def __init__(self, llm_annotations: dict = None):
        """
        Args:
            llm_annotations: Optional dict of LLM-generated chart annotations.
                Keys: 'volume_hist', 'crypto_metrics', 'benford_law', 'vv_correlation'
                Values: list of annotation dicts with 'type', 'value', 'label' fields.
        """
        self.llm_annotations = llm_annotations or {}

    def _make_volume_hist(self, data: pd.DataFrame, directory: str) -> None:
        """Generate volume histogram chart config."""
        volumes = data['volume'].dropna().tolist()

        # Compute histogram bins
        hist_values, bin_edges = np.histogram(volumes, bins=30)
        labels = [f"{bin_edges[i]:.0f}-{bin_edges[i+1]:.0f}" for i in range(len(hist_values))]

        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Frequency",
                    "data": hist_values.tolist(),
                    "backgroundColor": "rgba(135, 206, 235, 0.7)",
                    "borderColor": "rgb(0, 0, 0)",
                    "borderWidth": 1,
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Transaction Volume Distribution"},
                    "annotation": self._build_annotations('volume_hist'),
                },
                "scales": {
                    "x": {"title": {"display": True, "text": "Transaction Volume"}},
                    "y": {"title": {"display": True, "text": "Frequency"}},
                },
            },
        }

        self._save_config(config, directory, 'volume_hist.json')

    def _make_crypto_metrics(self, data: pd.DataFrame, directory: str) -> None:
        """Generate 4-panel crypto metrics chart config (volume, trade count, avg tx size, buy/sell ratio)."""
        timestamps = [ts.isoformat() for ts in data.index]

        # Use separate chart configs for each metric (Chart.js doesn't support subplots natively)
        metrics = [
            ('volume', 'Volume', 'rgba(54, 162, 235, 0.8)', 'Volume Over Time'),
            ('tradecount', 'Trade Count', 'rgba(75, 192, 75, 0.8)', 'Trade Count Over Time'),
            ('avgtransactionsize', 'Avg Transaction Size', 'rgba(255, 159, 64, 0.8)', 'Avg Transaction Size Over Time'),
            ('buysellratio', 'Buy/Sell Ratio', 'rgba(255, 99, 132, 0.8)', 'Buy/Sell Ratio Over Time'),
        ]

        for col, label, color, title in metrics:
            values = data[col].fillna(0).tolist()
            config = {
                "type": "line",
                "data": {
                    "labels": timestamps,
                    "datasets": [{
                        "label": label,
                        "data": values,
                        "borderColor": color,
                        "backgroundColor": color.replace('0.8', '0.1'),
                        "fill": True,
                        "tension": 0.1,
                        "pointRadius": 0,
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"display": True, "text": title},
                        "annotation": self._build_annotations(f'crypto_metrics_{col}'),
                    },
                    "scales": {
                        "x": {
                            "type": "time",
                            "time": {"unit": "hour", "displayFormats": {"hour": "MM/dd HH:mm"}},
                            "title": {"display": True, "text": "Timestamp"},
                        },
                        "y": {"title": {"display": True, "text": label}},
                    },
                },
            }
            self._save_config(config, directory, f'crypto_{col}.json')

    def _make_benfordlaw(self, data: pd.DataFrame, directory: str) -> None:
        """Generate Benford's Law chart config with dual axes."""
        timestamps = [ts.isoformat() for ts in data.index]
        benford_scores = data['benfordlawtest'].fillna(0).tolist()
        critical_values = (1.36 / np.sqrt(data['tradecount'].replace(0, 1))).tolist()

        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Benford Law Test Score",
                        "data": benford_scores,
                        "borderColor": "rgb(54, 162, 235)",
                        "backgroundColor": "rgba(54, 162, 235, 0.1)",
                        "fill": False,
                        "tension": 0.1,
                        "pointRadius": 0,
                        "yAxisID": "y",
                    },
                    {
                        "label": "K-S Critical Value (α=0.05)",
                        "data": critical_values,
                        "borderColor": "rgb(75, 192, 75)",
                        "backgroundColor": "rgba(75, 192, 75, 0.1)",
                        "fill": False,
                        "tension": 0.1,
                        "pointRadius": 0,
                        "borderDash": [5, 5],
                        "yAxisID": "y1",
                    },
                ]
            },
            "options": {
                "responsive": True,
                "interaction": {"mode": "index", "intersect": False},
                "plugins": {
                    "title": {"display": True, "text": "Benford Law Test Score vs Critical Value"},
                    "annotation": self._build_annotations('benford_law'),
                },
                "scales": {
                    "x": {
                        "type": "time",
                        "time": {"unit": "day", "displayFormats": {"day": "yyyy-MM-dd"}},
                        "title": {"display": True, "text": "Timestamp"},
                    },
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {"display": True, "text": "Benford Law Test Score"},
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {"display": True, "text": "K-S Critical Value"},
                        "grid": {"drawOnChartArea": False},
                    },
                },
            },
        }

        self._save_config(config, directory, 'benford_law.json')

    def _make_vvcorrelation(self, data: pd.DataFrame, directory: str) -> None:
        """Generate volume-volatility correlation chart config."""
        timestamps = [ts.isoformat() for ts in data.index]
        vv_values = data['vvcorrelation'].fillna(0).tolist()

        config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [{
                    "label": "VV Correlation",
                    "data": vv_values,
                    "borderColor": "rgb(128, 0, 128)",
                    "backgroundColor": "rgba(128, 0, 128, 0.1)",
                    "fill": True,
                    "tension": 0.1,
                    "pointRadius": 2,
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {"display": True, "text": "Volume-Volatility Correlation Over Time"},
                    "annotation": self._build_annotations('vv_correlation'),
                },
                "scales": {
                    "x": {
                        "type": "time",
                        "time": {"unit": "day", "displayFormats": {"day": "yyyy-MM-dd"}},
                        "title": {"display": True, "text": "Timestamp"},
                    },
                    "y": {
                        "title": {"display": True, "text": "VV Correlation"},
                        "suggestedMin": -1,
                        "suggestedMax": 1,
                    },
                },
            },
        }

        # Add threshold line at 0.4 (suspicion threshold)
        if 'annotation' not in config['options']['plugins']:
            config['options']['plugins']['annotation'] = {"annotations": {}}
        config['options']['plugins']['annotation']['annotations']['threshold'] = {
            "type": "line",
            "yMin": 0.4,
            "yMax": 0.4,
            "borderColor": "rgba(255, 0, 0, 0.5)",
            "borderWidth": 2,
            "borderDash": [6, 6],
            "label": {
                "display": True,
                "content": "Suspicion Threshold (0.4)",
                "position": "end",
            },
        }

        self._save_config(config, directory, 'vv_correlation.json')

    def _build_annotations(self, chart_key: str) -> dict:
        """Build Chart.js annotation plugin config from LLM annotations."""
        annotations_list = self.llm_annotations.get(chart_key, [])
        if not annotations_list:
            return {}

        annotations = {}
        for i, ann in enumerate(annotations_list):
            ann_type = ann.get('type', 'line')
            if ann_type == 'line':
                annotations[f'ann_{i}'] = {
                    "type": "line",
                    "yMin": ann.get('value', 0),
                    "yMax": ann.get('value', 0),
                    "borderColor": ann.get('color', 'rgba(255, 0, 0, 0.7)'),
                    "borderWidth": 2,
                    "borderDash": [4, 4],
                    "label": {
                        "display": True,
                        "content": ann.get('label', ''),
                        "position": "end",
                    },
                }
            elif ann_type == 'box':
                annotations[f'ann_{i}'] = {
                    "type": "box",
                    "xMin": ann.get('xMin'),
                    "xMax": ann.get('xMax'),
                    "backgroundColor": ann.get('color', 'rgba(255, 0, 0, 0.1)'),
                    "borderColor": ann.get('borderColor', 'rgba(255, 0, 0, 0.3)'),
                    "label": {
                        "display": True,
                        "content": ann.get('label', ''),
                    },
                }
        return {"annotations": annotations}

    def _save_config(self, config: dict, directory: str, filename: str) -> None:
        """Save Chart.js configuration to JSON file."""
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)
        print(f"Chart config saved: {filepath}")

    def generate_report(self, data, directory: str) -> list:
        """
        Generate all chart configuration JSON files.

        Returns list of generated filenames for use in markdown template.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        self._make_volume_hist(df, directory)
        self._make_crypto_metrics(df, directory)
        self._make_benfordlaw(df, directory)
        self._make_vvcorrelation(df, directory)

        return [
            'volume_hist.json',
            'crypto_volume.json',
            'crypto_tradecount.json',
            'crypto_avgtransactionsize.json',
            'crypto_buysellratio.json',
            'benford_law.json',
            'vv_correlation.json',
        ]
