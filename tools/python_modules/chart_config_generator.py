"""
Chart Configuration Generator for Market Health Reporter

Generates Chart.js compatible JSON configurations from market data.
These configs can be embedded in Hugo articles using the chart shortcode.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any


class ChartConfigGenerator:
    """Generates Chart.js configuration objects from market data."""
    
    def __init__(self):
        self.colors = {
            'blue': 'rgba(54, 162, 235, 0.7)',
            'green': 'rgba(75, 192, 192, 0.7)',
            'orange': 'rgba(255, 159, 64, 0.7)',
            'red': 'rgba(255, 99, 132, 0.7)',
            'purple': 'rgba(153, 102, 255, 0.7)',
            'yellow': 'rgba(255, 206, 86, 0.7)',
        }
        
        self.border_colors = {
            'blue': 'rgba(54, 162, 235, 1)',
            'green': 'rgba(75, 192, 192, 1)',
            'orange': 'rgba(255, 159, 64, 1)',
            'red': 'rgba(255, 99, 132, 1)',
            'purple': 'rgba(153, 102, 255, 1)',
            'yellow': 'rgba(255, 206, 86, 1)',
        }

    def _format_timestamps(self, timestamps: pd.DatetimeIndex) -> List[str]:
        """Format timestamps for Chart.js labels."""
        return [ts.strftime('%Y-%m-%d %H:%M') for ts in timestamps]

    def generate_volume_histogram(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate histogram config for volume distribution.
        
        Replaces: _make_volume_hist (volume_hist.png)
        """
        volumes = data['volume'].values
        
        # Calculate histogram bins
        hist, bin_edges = np.histogram(volumes, bins=30)
        bin_labels = [f'{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}' 
                      for i in range(len(bin_edges)-1)]
        
        config = {
            "type": "bar",
            "data": {
                "labels": bin_labels,
                "datasets": [{
                    "label": "Frequency",
                    "data": hist.tolist(),
                    "backgroundColor": self.colors['blue'],
                    "borderColor": self.border_colors['blue'],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Transaction Volume Distribution"
                    },
                    "legend": {
                        "display": False
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Transaction Volume"
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": "Frequency"
                        },
                        "beginAtZero": True
                    }
                }
            }
        }
        return config

    def generate_crypto_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate multi-line chart config for cryptocurrency metrics over time.
        
        Replaces: _make_crypto_metrics (crypto_metrics.png)
        """
        labels = self._format_timestamps(data.index)
        
        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Volume",
                        "data": data['volume'].tolist(),
                        "borderColor": self.border_colors['blue'],
                        "backgroundColor": self.colors['blue'],
                        "yAxisID": "y",
                        "tension": 0.1
                    },
                    {
                        "label": "Trade Count",
                        "data": data['tradecount'].tolist(),
                        "borderColor": self.border_colors['green'],
                        "backgroundColor": self.colors['green'],
                        "yAxisID": "y1",
                        "tension": 0.1
                    },
                    {
                        "label": "Avg Transaction Size",
                        "data": data['avgtransactionsize'].tolist(),
                        "borderColor": self.border_colors['orange'],
                        "backgroundColor": self.colors['orange'],
                        "yAxisID": "y2",
                        "tension": 0.1
                    },
                    {
                        "label": "Buy/Sell Ratio",
                        "data": data['buysellratio'].tolist(),
                        "borderColor": self.border_colors['red'],
                        "backgroundColor": self.colors['red'],
                        "yAxisID": "y3",
                        "tension": 0.1
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "interaction": {
                    "mode": "index",
                    "intersect": False
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Cryptocurrency Metrics Over Time"
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Timestamp"
                        },
                        "ticks": {
                            "maxRotation": 45,
                            "minRotation": 45
                        }
                    },
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {
                            "display": True,
                            "text": "Volume"
                        }
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {
                            "display": True,
                            "text": "Trade Count"
                        },
                        "grid": {
                            "drawOnChartArea": False
                        }
                    },
                    "y2": {
                        "type": "linear",
                        "display": False,
                        "position": "left"
                    },
                    "y3": {
                        "type": "linear",
                        "display": False,
                        "position": "right"
                    }
                }
            }
        }
        return config

    def generate_benford_law(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate dual-axis chart for Benford Law test score and trade count.
        
        Replaces: _make_benfordlaw (benford_law.png)
        """
        labels = self._format_timestamps(data.index)
        
        # Calculate critical values
        critical_values = (1.36 / np.sqrt(data['tradecount'])).tolist()
        
        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Benford Law Test Score",
                        "data": data['benfordlawtest'].tolist(),
                        "borderColor": self.border_colors['blue'],
                        "backgroundColor": self.colors['blue'],
                        "yAxisID": "y",
                        "tension": 0.1
                    },
                    {
                        "label": "Critical Value (1.36/√tradecount)",
                        "data": critical_values,
                        "borderColor": self.border_colors['green'],
                        "backgroundColor": self.colors['green'],
                        "yAxisID": "y1",
                        "tension": 0.1,
                        "borderDash": [5, 5]
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "interaction": {
                    "mode": "index",
                    "intersect": False
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Benford Law Test Score and Critical Value Over Time"
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Timestamp"
                        },
                        "ticks": {
                            "maxRotation": 45,
                            "minRotation": 45
                        }
                    },
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {
                            "display": True,
                            "text": "Benford Law Test Score"
                        }
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {
                            "display": True,
                            "text": "Critical Value"
                        },
                        "grid": {
                            "drawOnChartArea": False
                        }
                    }
                }
            }
        }
        return config

    def generate_vv_correlation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate line chart for Volume-Volatility correlation.
        
        Replaces: _make_vvcorrelation (vv_correlation.png)
        """
        labels = self._format_timestamps(data.index)
        
        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "VV Correlation",
                    "data": data['vvcorrelation'].tolist(),
                    "borderColor": self.border_colors['purple'],
                    "backgroundColor": self.colors['purple'],
                    "tension": 0.1,
                    "fill": False
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "VV Correlation Over Time"
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Timestamp"
                        },
                        "ticks": {
                            "maxRotation": 45,
                            "minRotation": 45
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": "VV Correlation"
                        }
                    }
                }
            }
        }
        return config

    def generate_all_charts(self, data: dict) -> Dict[str, Dict[str, Any]]:
        """Generate all chart configurations from raw market data.
        
        Args:
            data: Raw market data dictionary
            
        Returns:
            Dictionary with chart IDs as keys and Chart.js configs as values
        """
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        return {
            'volume_hist': self.generate_volume_histogram(df),
            'crypto_metrics': self.generate_crypto_metrics(df),
            'benford_law': self.generate_benford_law(df),
            'vv_correlation': self.generate_vv_correlation(df)
        }

    def config_to_json(self, config: Dict[str, Any], indent: int = 2) -> str:
        """Convert config dict to JSON string for embedding."""
        return json.dumps(config, indent=indent)

    def generate_shortcode(self, chart_id: str, config: Dict[str, Any]) -> str:
        """Generate Hugo shortcode string for embedding in markdown.
        
        Args:
            chart_id: Unique identifier for the chart
            config: Chart.js configuration object
            
        Returns:
            Hugo shortcode string like: {{< chart id="..." config=`{...}` />}}
        """
        config_json = self.config_to_json(config)
        return f'{{{{< chart id="{chart_id}" config=`{config_json}` />}}}}'


# Convenience function for direct use
def generate_chart_configs(data: dict) -> Dict[str, Dict[str, Any]]:
    """Generate all chart configurations from market data."""
    generator = ChartConfigGenerator()
    return generator.generate_all_charts(data)


def generate_chart_shortcodes(data: dict) -> Dict[str, str]:
    """Generate Hugo shortcodes for all charts from market data."""
    generator = ChartConfigGenerator()
    configs = generator.generate_all_charts(data)
    return {
        chart_id: generator.generate_shortcode(chart_id, config)
        for chart_id, config in configs.items()
    }
