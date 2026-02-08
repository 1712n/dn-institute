import pandas as pd
import numpy as np
import json
import os


class Visualization:
    def __init__(self):
        pass

    def _save_json(self, data_dict, filename, directory):
        """Save chart data as JSON for dynamic rendering."""
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2)

    def _make_volume_hist(self, data, directory):
        """Generate JSON data for volume histogram."""
        hist, bin_edges = np.histogram(data['volume'], bins=30)

        chart_data = {
            'type': 'volume_histogram',
            'title': 'Transaction Volume Distribution',
            'data': {
                'labels': [f'{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}' for i in range(len(bin_edges)-1)],
                'values': hist.tolist(),
                'bins': bin_edges.tolist()
            },
            'options': {
                'xlabel': 'Transaction Volume',
                'ylabel': 'Frequency'
            }
        }
        self._save_json(chart_data, 'volume_hist.json', directory)

    def _make_crypto_metrics(self, data, directory):
        """Generate JSON data for crypto metrics time series."""
        chart_data = {
            'type': 'multi_line_chart',
            'title': 'Cryptocurrency Metrics Over Time',
            'data': {
                'timestamps': data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'datasets': [
                    {
                        'label': 'Volume',
                        'values': data['volume'].tolist(),
                        'color': 'rgb(54, 162, 235)',
                        'yAxisID': 'y1'
                    },
                    {
                        'label': 'Trade Count',
                        'values': data['tradecount'].tolist(),
                        'color': 'rgb(75, 192, 192)',
                        'yAxisID': 'y2'
                    },
                    {
                        'label': 'Avg Transaction Size',
                        'values': data['avgtransactionsize'].tolist(),
                        'color': 'rgb(255, 159, 64)',
                        'yAxisID': 'y3'
                    },
                    {
                        'label': 'Buy/Sell Ratio',
                        'values': data['buysellratio'].tolist(),
                        'color': 'rgb(255, 99, 132)',
                        'yAxisID': 'y4'
                    }
                ]
            }
        }
        self._save_json(chart_data, 'crypto_metrics.json', directory)

    def _make_benfordlaw(self, data, directory):
        """Generate JSON data for Benford Law chart."""
        # Calculate the derived metric for trade count
        trade_count_metric = (1.36 / np.sqrt(data['tradecount'])).tolist()

        chart_data = {
            'type': 'dual_axis_line',
            'title': 'Benford Law Test Score and Trade Count Over Time',
            'data': {
                'timestamps': data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'datasets': [
                    {
                        'label': 'Benford Law Test Score',
                        'values': data['benfordlawtest'].tolist(),
                        'color': 'rgb(54, 162, 235)',
                        'yAxisID': 'y-left'
                    },
                    {
                        'label': 'Trade Count (1.36/√n)',
                        'values': trade_count_metric,
                        'color': 'rgb(75, 192, 192)',
                        'yAxisID': 'y-right'
                    }
                ]
            }
        }
        self._save_json(chart_data, 'benford_law.json', directory)

    def _make_vvcorrelation(self, data, directory):
        """Generate JSON data for VV correlation chart."""
        chart_data = {
            'type': 'line_chart',
            'title': 'VV Correlation Over Time',
            'data': {
                'timestamps': data.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'datasets': [
                    {
                        'label': 'VV Correlation',
                        'values': data['vvcorrelation'].tolist(),
                        'color': 'rgb(153, 102, 255)'
                    }
                ]
            },
            'options': {
                'xlabel': 'Timestamp',
                'ylabel': 'VV Correlation'
            }
        }
        self._save_json(chart_data, 'vv_correlation.json', directory)

    def generate_report(self, data, directory):
        """Generate JSON data files for all charts."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        data = pd.DataFrame(data)
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.set_index('timestamp', inplace=True)

        self._make_volume_hist(data, directory)
        self._make_crypto_metrics(data, directory)
        self._make_benfordlaw(data, directory)
        self._make_vvcorrelation(data, directory)