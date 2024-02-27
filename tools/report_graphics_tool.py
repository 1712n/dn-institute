import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import os


class Visualization:
    def __init__(self):
        pass


    def _make_volume_hist(self, data, directory):
        plt.figure(figsize=(10, 6))
        plt.hist(data['volume'], bins=30, color='skyblue', edgecolor='black')
        plt.xlabel('Transaction Volume')
        plt.ylabel('Frequency')
        plt.title('Transaction Volume Distribution')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.savefig(os.path.join(directory, 'volume_hist.png'))
        plt.close()


    def _make_crypto_metrics(self, data, directory):
        fig, axs = plt.subplots(4, 1, figsize=(15, 10), sharex=True)

        axs[0].plot(data.index, data['volume'], label='Volume', color='blue')
        axs[0].set_ylabel('Volume')

        axs[1].plot(data.index, data['tradecount'], label='Trade Count', color='green')
        axs[1].set_ylabel('Trade Count')

        axs[2].plot(data.index, data['avgtransactionsize'], label='Avg Transaction Size', color='orange')
        axs[2].set_ylabel('Avg Transaction Size')

        axs[3].plot(data.index, data['buysellratio'], label='Buy/Sell Ratio', color='red')
        axs[3].set_ylabel('Buy/Sell Ratio')

        axs[3].set_xlabel('Timestamp')

        fig.suptitle('Cryptocurrency Metrics Over Time')

        for ax in axs:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(os.path.join(directory, 'crypto_metrics.png'))
        plt.close()
        

    def _make_benfordlaw(self, data, directory):
        fig, ax1 = plt.subplots(figsize=(15, 10), layout='constrained')
        ax1.plot(data.index, data['benfordlawtest'], color='blue', linestyle='-', label='Benford Law Test Score')
        ax1.set_xlabel('Timestamp')
        ax1.set_ylabel('Benford Law Test Score', color='blue')
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=24))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax2 = ax1.twinx()
        ax2.plot(data.index, 1.36 / np.sqrt(data['tradecount']), color='green', linestyle='-', label='Trade Count')
        ax2.set_ylabel('Trade Count', color='green')
        ax1.set_title('Benford Law Test Score and Trade Count Over Time')
        lines = ax1.get_lines() + ax2.get_lines()
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc='upper left')
        plt.savefig(os.path.join(directory, 'benford_law.png'))
        plt.close()


    def _make_vvcorrelation(self, data, directory):
        fig, ax = plt.subplots(figsize=(15, 10), layout='constrained')
        ax.plot(data.index, data['vvcorrelation'], color='purple', linestyle='-', marker='o', label='VV Correlation')
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=24))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('VV Correlation')
        ax.set_title('VV Correlation Over Time')
        ax.legend()
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(directory, 'vv_correlation.png'))
        plt.close()

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