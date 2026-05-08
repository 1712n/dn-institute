import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np
import os


class Visualization:
    def __init__(self):
        pass

    def _make_volume_hist(self, data, directory):
        """Generate interactive volume histogram using Plotly."""
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=data['volume'],
            nbinsx=30,
            marker_color='skyblue',
            marker_line_color='black',
            marker_line_width=1,
            name='Frequency',
            hovertemplate='Volume Range: %{x}<br>Frequency: %{y}<extra></extra>'
        ))
        fig.update_layout(
            title='Transaction Volume Distribution',
            xaxis_title='Transaction Volume',
            yaxis_title='Frequency',
            template='plotly_white',
            height=500,
            margin=dict(l=60, r=40, t=60, b=60),
            hovermode='x unified'
        )
        html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        with open(os.path.join(directory, 'volume_hist.plotly'), 'w', encoding='utf-8') as f:
            f.write(html)

    def _make_crypto_metrics(self, data, directory):
        """Generate interactive crypto metrics charts (4 separate .plotly files)."""
        # 1. Volume over time
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=data.index,
            y=data['volume'],
            mode='lines',
            name='Volume',
            line=dict(color='blue'),
            hovertemplate='Time: %{x}<br>Volume: %{y:.2f}<extra></extra>'
        ))
        fig_vol.update_layout(
            title='Transaction Volume Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Volume',
            template='plotly_white',
            height=400,
            margin=dict(l=60, r=40, t=60, b=60)
        )
        with open(os.path.join(directory, 'crypto_volume.plotly'), 'w', encoding='utf-8') as f:
            f.write(pio.to_html(fig_vol, full_html=False, include_plotlyjs=False))

        # 2. Trade count over time
        fig_tc = go.Figure()
        fig_tc.add_trace(go.Scatter(
            x=data.index,
            y=data['tradecount'],
            mode='lines',
            name='Trade Count',
            line=dict(color='green'),
            hovertemplate='Time: %{x}<br>Trade Count: %{y:.0f}<extra></extra>'
        ))
        fig_tc.update_layout(
            title='Trade Count Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Trade Count',
            template='plotly_white',
            height=400,
            margin=dict(l=60, r=40, t=60, b=60)
        )
        with open(os.path.join(directory, 'crypto_tradecount.plotly'), 'w', encoding='utf-8') as f:
            f.write(pio.to_html(fig_tc, full_html=False, include_plotlyjs=False))

        # 3. Average transaction size over time
        fig_avg = go.Figure()
        fig_avg.add_trace(go.Scatter(
            x=data.index,
            y=data['avgtransactionsize'],
            mode='lines',
            name='Avg Transaction Size',
            line=dict(color='orange'),
            hovertemplate='Time: %{x}<br>Avg Tx Size: %{y:.2f}<extra></extra>'
        ))
        fig_avg.update_layout(
            title='Average Transaction Size Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Avg Transaction Size',
            template='plotly_white',
            height=400,
            margin=dict(l=60, r=40, t=60, b=60)
        )
        with open(os.path.join(directory, 'crypto_avg_txs.plotly'), 'w', encoding='utf-8') as f:
            f.write(pio.to_html(fig_avg, full_html=False, include_plotlyjs=False))

        # 4. Buy/Sell ratio over time
        fig_bs = go.Figure()
        fig_bs.add_trace(go.Scatter(
            x=data.index,
            y=data['buysellratio'],
            mode='lines',
            name='Buy/Sell Ratio',
            line=dict(color='red'),
            hovertemplate='Time: %{x}<br>Buy/Sell Ratio: %{y:.2f}<extra></extra>'
        ))
        fig_bs.update_layout(
            title='Buy/Sell Ratio Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Buy/Sell Ratio',
            template='plotly_white',
            height=400,
            margin=dict(l=60, r=40, t=60, b=60)
        )
        with open(os.path.join(directory, 'crypto_buysell.plotly'), 'w', encoding='utf-8') as f:
            f.write(pio.to_html(fig_bs, full_html=False, include_plotlyjs=False))

    def _make_benfordlaw(self, data, directory):
        """Generate interactive Benford's Law chart with dual y-axis."""
        # Convert index to string to avoid datetime parsing issues
        x_vals = [str(idx) for idx in data.index]
        crit_val = 1.36 / np.sqrt(data['tradecount'])

        fig = go.Figure()

        # Benford Law Test Score line
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=data['benfordlawtest'],
            mode='lines',
            name='Benford Law Test Score',
            line=dict(color='blue'),
            yaxis='y',
            hovertemplate='Time: %{x}<br>Benford Score: %{y:.4f}<extra></extra>'
        ))

        # Critical value line (trade count derived)
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=crit_val,
            mode='lines',
            name='Critical Value',
            line=dict(color='green', dash='dash'),
            yaxis='y2',
            hovertemplate='Time: %{x}<br>Critical Value: %{y:.4f}<extra></extra>'
        ))

        fig.update_layout(
            title="Benford's Law Test Score and Critical Value Over Time",
            xaxis=dict(
                title='Timestamp',
                showticklabels=True,
                tickangle=45
            ),
            yaxis=dict(
                title='Benford Law Test Score',
                titlefont=dict(color='blue'),
                tickfont=dict(color='blue'),
                side='left'
            ),
            yaxis2=dict(
                title='Critical Value',
                titlefont=dict(color='green'),
                tickfont=dict(color='green'),
                side='right',
                overlaying='y',
                showgrid=False
            ),
            template='plotly_white',
            height=500,
            margin=dict(l=60, r=60, t=60, b=100),
            legend=dict(x=0.5, y=1.12, xanchor='center', orientation='h'),
            hovermode='x unified'
        )
        with open(os.path.join(directory, 'benford_law.plotly'), 'w', encoding='utf-8') as f:
            f.write(pio.to_html(fig, full_html=False, include_plotlyjs=False))

    def _make_vvcorrelation(self, data, directory):
        """Generate interactive VV Correlation chart."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['vvcorrelation'],
            mode='lines+markers',
            name='VV Correlation',
            line=dict(color='purple'),
            marker=dict(size=4, symbol='circle'),
            hovertemplate='Time: %{x}<br>VV Correlation: %{y:.4f}<extra></extra>'
        ))

        # Add reference lines for context
        fig.add_hline(
            y=0.4, line_dash='dash', line_color='red',
            annotation_text='Low threshold (0.4)', annotation_position='bottom right'
        )
        fig.add_hline(
            y=0.7, line_dash='dash', line_color='gray',
            annotation_text='High threshold (0.7)', annotation_position='top right'
        )

        fig.update_layout(
            title='Volume-Volatility Correlation Over Time',
            xaxis_title='Timestamp',
            yaxis_title='VV Correlation',
            template='plotly_white',
            height=500,
            margin=dict(l=60, r=40, t=60, b=80),
            hovermode='x unified'
        )
        with open(os.path.join(directory, 'vv_correlation.plotly'), 'w', encoding='utf-8') as f:
            f.write(pio.to_html(fig, full_html=False, include_plotlyjs=False))

    def generate_report(self, data, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        data = pd.DataFrame(data)
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.set_index('timestamp', inplace=True)

        self._make_volume_hist(data, directory)
        self._make_crypto_metrics(data, directory)
        self._make_benfordlaw(data, directory)
        self._make_vvcorrelation(data, directory)
