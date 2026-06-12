"""
Analyze crypto market data for wash trading indicators.
Generates charts for the volume-price divergence article.

Metrics:
1. Volume-Price Correlation (rolling window)
2. Volume/Price Impact Ratio
3. Trade Size Distribution (Benford's Law + KS test)
4. Cross-Exchange Volume Divergence
5. Order Book Depth Analysis
6. Trade Interval Entropy
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
from collections import Counter
import os
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE, "data")
IMG_DIR = os.path.join(BASE, "images")
os.makedirs(IMG_DIR, exist_ok=True)

# Style
plt.rcParams.update({
    'figure.figsize': (12, 6),
    'figure.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

COLORS = {
    'BTCUSDT': '#F7931A',
    'ETHUSDT': '#627EEA',
    'SOLUSDT': '#9945FF',
    'DOGEUSDT': '#C2A633',
}


def load_klines():
    """Load and prepare klines data."""
    df = pd.read_csv(os.path.join(DATA_DIR, "binance_klines_1h.csv"))
    df["open_time"] = pd.to_datetime(df["open_time"])
    return df


def load_coingecko_exchanges():
    """Load CoinGecko exchange data for all coins."""
    all_data = []
    for coin in ["bitcoin", "ethereum", "solana", "dogecoin"]:
        path = os.path.join(DATA_DIR, f"coingecko_{coin}_exchanges.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["coin"] = coin
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()


# ============================================================
# Chart 1: Volume-Price Correlation (Rolling Window)
# ============================================================

def chart_volume_price_correlation(df):
    """
    Rolling correlation between volume and |price change|.
    Genuine markets: positive correlation (volume accompanies price moves).
    Wash trading: decorrelation (volume without price impact).
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Rolling Volume-Price Correlation (48h Window)\n"
                 "Low correlation suggests artificial volume",
                 fontsize=15, fontweight='bold')

    for idx, symbol in enumerate(SYMBOLS):
        ax = axes[idx // 2][idx % 2]
        sym_df = df[df["symbol"] == symbol].copy()
        sym_df = sym_df.sort_values("open_time").reset_index(drop=True)

        # Rolling correlation
        window = 48
        sym_df["vol_price_corr"] = (
            sym_df["volume_usd"]
            .rolling(window)
            .corr(sym_df["abs_price_change"])
        )

        ax.plot(sym_df["open_time"], sym_df["vol_price_corr"],
                color=COLORS[symbol], linewidth=0.8, alpha=0.9)
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=0.8)
        ax.axhline(y=0.3, color='green', linestyle=':', alpha=0.4, linewidth=0.8)
        ax.fill_between(sym_df["open_time"], sym_df["vol_price_corr"], 0,
                        where=sym_df["vol_price_corr"] < 0,
                        alpha=0.2, color='red')
        ax.set_title(f"{symbol.replace('USDT', '/USDT')}", fontweight='bold')
        ax.set_ylabel("Correlation")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.set_ylim(-0.6, 0.8)

        # Stats
        mean_corr = sym_df["vol_price_corr"].mean()
        pct_negative = (sym_df["vol_price_corr"] < 0).mean() * 100
        ax.text(0.02, 0.05,
                f"Mean: {mean_corr:.3f}\nNegative: {pct_negative:.1f}%",
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "volume_price_correlation.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Chart 2: Volume/Price Impact Ratio
# ============================================================

def chart_volume_price_impact(df):
    """
    Volume per unit of price movement.
    High ratio = volume without proportional price impact = suspicious.
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle("Volume/Price Impact Ratio Over Time\n"
                 "Higher values indicate volume without price movement (wash trading signal)",
                 fontsize=14, fontweight='bold')

    for symbol in SYMBOLS:
        sym_df = df[df["symbol"] == symbol].copy().sort_values("open_time")
        # Avoid division by zero
        sym_df["impact_ratio"] = sym_df["volume_usd"] / (sym_df["abs_price_change"] + 1e-10)
        # Normalize to median for comparison
        median_ratio = sym_df["impact_ratio"].median()
        sym_df["norm_ratio"] = sym_df["impact_ratio"] / median_ratio

        # Rolling average for smoothing
        sym_df["smooth_ratio"] = sym_df["norm_ratio"].rolling(24, min_periods=1).mean()

        ax.plot(sym_df["open_time"], sym_df["smooth_ratio"],
                label=symbol.replace("USDT", "/USDT"),
                color=COLORS[symbol], linewidth=1.5, alpha=0.85)

    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label="Median baseline")
    ax.axhline(y=3, color='red', linestyle=':', alpha=0.5, label="3x median (anomaly threshold)")
    ax.set_ylabel("Normalized Volume/Price Impact Ratio")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.legend(loc='upper right')
    ax.set_ylim(0, 8)

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "volume_price_impact_ratio.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Chart 3: Trade Size Distribution (Benford's Law)
# ============================================================

def benford_expected():
    """Expected Benford's Law distribution."""
    return {d: np.log10(1 + 1/d) for d in range(1, 10)}


def first_digit_dist(values):
    """Get first digit distribution from a series of values."""
    digits = []
    for v in values:
        if v > 0:
            first = int(str(f"{v:.10f}").lstrip('0').lstrip('.')[0])
            if 1 <= first <= 9:
                digits.append(first)
    if not digits:
        return {d: 0 for d in range(1, 10)}
    counts = Counter(digits)
    total = sum(counts.values())
    return {d: counts.get(d, 0) / total for d in range(1, 10)}


def chart_benford_analysis(df):
    """
    Benford's Law analysis of trade volumes.
    Genuine data follows Benford's distribution; wash trading deviates.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Benford's Law Analysis of Hourly Trade Volumes\n"
                 "Deviation from expected distribution suggests synthetic data",
                 fontsize=14, fontweight='bold')

    benford = benford_expected()
    benford_vals = [benford[d] for d in range(1, 10)]

    ks_results = {}

    for idx, symbol in enumerate(SYMBOLS):
        ax = axes[idx // 2][idx % 2]
        sym_df = df[df["symbol"] == symbol].copy()

        # Get first digit distribution of volume
        observed = first_digit_dist(sym_df["volume_usd"].values)
        obs_vals = [observed[d] for d in range(1, 10)]

        # KS test
        obs_digits = []
        for v in sym_df["volume_usd"].values:
            if v > 0:
                first = int(str(f"{v:.10f}").lstrip('0').lstrip('.')[0])
                if 1 <= first <= 9:
                    obs_digits.append(first)
        ks_stat, ks_p = stats.kstest(obs_digits, 'uniform', args=(0.5, 8.5))

        ks_results[symbol] = {"stat": ks_stat, "p": ks_p}

        x = np.arange(1, 10)
        width = 0.35
        ax.bar(x - width/2, benford_vals, width, label="Benford Expected",
               color='steelblue', alpha=0.7)
        ax.bar(x + width/2, obs_vals, width, label="Observed",
               color=COLORS[symbol], alpha=0.8)
        ax.set_xlabel("Leading Digit")
        ax.set_ylabel("Frequency")
        ax.set_title(f"{symbol.replace('USDT', '/USDT')}", fontweight='bold')
        ax.set_xticks(x)
        ax.legend(fontsize=9)

        # Add KS test result
        color = 'green' if ks_p > 0.05 else 'red'
        ax.text(0.98, 0.95,
                f"KS p-value: {ks_p:.4f}\n{'Normal' if ks_p > 0.05 else 'Anomalous'}",
                transform=ax.transAxes, fontsize=10, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
                color=color, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "benford_analysis.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")

    return ks_results


# ============================================================
# Chart 4: Cross-Exchange Volume Divergence
# ============================================================

def chart_cross_exchange_divergence(exch_df):
    """
    Analyze volume distribution across exchanges.
    Legitimate tokens show distributed volume; wash trading concentrates on specific venues.
    """
    if exch_df.empty:
        print("  Skipping cross-exchange chart (no data)")
        return

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Cross-Exchange Volume Distribution\n"
                 "Volume concentration and trust score analysis",
                 fontsize=14, fontweight='bold')

    coin_names = {"bitcoin": "BTC", "ethereum": "ETH",
                  "solana": "SOL", "dogecoin": "DOGE"}

    for idx, (coin_id, label) in enumerate(coin_names.items()):
        ax = axes[idx // 2][idx % 2]
        coin_data = exch_df[exch_df["coin"] == coin_id].copy()
        coin_data = coin_data[coin_data["volume_24h"] > 0]
        coin_data = coin_data.nlargest(15, "volume_24h")

        # Color by trust score
        colors = []
        for _, row in coin_data.iterrows():
            if row.get("is_anomaly", False):
                colors.append("red")
            elif row.get("trust_score", "") == "green":
                colors.append("steelblue")
            elif row.get("trust_score", "") == "yellow":
                colors.append("orange")
            else:
                colors.append("gray")

        bars = ax.barh(range(len(coin_data)),
                       coin_data["volume_24h"].values / 1e6,
                       color=colors, alpha=0.8)
        ax.set_yticks(range(len(coin_data)))
        ax.set_yticklabels(coin_data["exchange"].values, fontsize=9)
        ax.set_xlabel("24h Volume (M USD)")
        ax.set_title(f"{label}/USD", fontweight='bold')
        ax.invert_yaxis()

        # Add trust indicators
        for i, (_, row) in enumerate(coin_data.iterrows()):
            anomaly = "⚠️" if row.get("is_anomaly", False) else ""
            ax.text(row["volume_24h"] / 1e6 + 0.5, i, anomaly, va='center', fontsize=12)

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "cross_exchange_volume.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Chart 5: Order Book Depth Analysis
# ============================================================

def chart_orderbook_analysis():
    """
    Analyze order book depth for signs of spoofing/layering.
    Look for unusual concentration at specific price levels.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Order Book Depth Analysis\n"
                 "Detecting potential spoofing/layering patterns",
                 fontsize=14, fontweight='bold')

    symbols = ["btcusdt", "ethusdt", "solusdt", "dogeusdt"]
    labels = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT"]

    for idx, (sym, label) in enumerate(zip(symbols, labels)):
        ax = axes[idx // 2][idx % 2]
        path = os.path.join(DATA_DIR, f"binance_orderbook_{sym}.csv")
        if not os.path.exists(path):
            continue

        ob = pd.read_csv(path)
        bids = ob[ob["side"] == "bid"].copy()
        asks = ob[ob["side"] == "ask"].copy()

        bids["price"] = bids["price"].astype(float)
        asks["price"] = asks["price"].astype(float)
        bids["qty"] = bids["qty"].astype(float)
        asks["qty"] = asks["qty"].astype(float)

        # Calculate cumulative depth
        bids["cum_qty"] = bids["qty"].cumsum()
        asks["cum_qty"] = asks["qty"].cumsum()

        # Normalize prices relative to mid price
        mid = (bids["price"].iloc[0] + asks["price"].iloc[0]) / 2
        bids["pct_from_mid"] = (bids["price"] - mid) / mid * 100
        asks["pct_from_mid"] = (asks["price"] - mid) / mid * 100

        ax.plot(bids["pct_from_mid"], bids["cum_qty"],
                color='green', linewidth=1.5, label='Bids')
        ax.plot(asks["pct_from_mid"], asks["cum_qty"],
                color='red', linewidth=1.5, label='Asks')
        ax.fill_between(bids["pct_from_mid"], bids["cum_qty"],
                        alpha=0.15, color='green')
        ax.fill_between(asks["pct_from_mid"], asks["cum_qty"],
                        alpha=0.15, color='red')
        ax.set_xlabel("Distance from Mid Price (%)")
        ax.set_ylabel("Cumulative Quantity")
        ax.set_title(label, fontweight='bold')
        ax.legend()

        # Calculate bid-ask imbalance
        bid_total = bids["qty"].sum()
        ask_total = asks["qty"].sum()
        imbalance = (bid_total - ask_total) / (bid_total + ask_total)
        ax.text(0.02, 0.95,
                f"Bid/Ask Imbalance: {imbalance:.3f}",
                transform=ax.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "orderbook_depth.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Chart 6: Trade Size Distribution Analysis
# ============================================================

def chart_trade_size_distribution(df):
    """
    Analyze distribution of average trade sizes.
    Power-law distribution expected; uniform/spiked = suspicious.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Average Trade Size Distribution (Hourly)\n"
                 "Power-law expected; spikes indicate bot activity",
                 fontsize=14, fontweight='bold')

    for idx, symbol in enumerate(SYMBOLS):
        ax = axes[idx // 2][idx % 2]
        sym_df = df[df["symbol"] == symbol].copy()
        avg_sizes = sym_df["avg_trade_size"].dropna()
        avg_sizes = avg_sizes[avg_sizes > 0]

        # Histogram with log scale
        ax.hist(avg_sizes, bins=50, color=COLORS[symbol],
                alpha=0.7, edgecolor='white', linewidth=0.5)
        ax.set_xlabel("Average Trade Size (USD)")
        ax.set_ylabel("Frequency")
        ax.set_title(f"{symbol.replace('USDT', '/USDT')}", fontweight='bold')

        # Add statistics
        mean_val = avg_sizes.mean()
        median_val = avg_sizes.median()
        std_val = avg_sizes.std()
        cv = std_val / mean_val  # Coefficient of variation
        ax.axvline(mean_val, color='red', linestyle='--', alpha=0.7, label=f'Mean: ${mean_val:,.0f}')
        ax.axvline(median_val, color='blue', linestyle='--', alpha=0.7, label=f'Median: ${median_val:,.0f}')
        ax.legend(fontsize=9)
        ax.text(0.98, 0.95,
                f"CV: {cv:.2f}\nStd: ${std_val:,.0f}",
                transform=ax.transAxes, fontsize=10, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "trade_size_distribution.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Chart 7: Volume Anomaly Detection (Z-Score)
# ============================================================

def chart_volume_anomaly(df):
    """
    Z-score based volume anomaly detection.
    Extreme z-scores indicate unusual volume activity.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Volume Z-Score Anomaly Detection\n"
                 "Values beyond ±3σ indicate statistically significant anomalies",
                 fontsize=14, fontweight='bold')

    for idx, symbol in enumerate(SYMBOLS):
        ax = axes[idx // 2][idx % 2]
        sym_df = df[df["symbol"] == symbol].copy().sort_values("open_time")

        # Calculate z-scores
        mean_vol = sym_df["volume_usd"].mean()
        std_vol = sym_df["volume_usd"].std()
        sym_df["vol_zscore"] = (sym_df["volume_usd"] - mean_vol) / std_vol

        # Plot
        colors = ['red' if z > 3 or z < -3 else COLORS[symbol] for z in sym_df["vol_zscore"]]
        ax.bar(sym_df["open_time"], sym_df["vol_zscore"],
               color=colors, alpha=0.7, width=0.04)
        ax.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='±3σ threshold')
        ax.axhline(y=-3, color='red', linestyle='--', alpha=0.5)
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        ax.set_ylabel("Volume Z-Score")
        ax.set_title(f"{symbol.replace('USDT', '/USDT')}", fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.legend(fontsize=9)

        # Count anomalies
        n_anomalies = ((sym_df["vol_zscore"] > 3) | (sym_df["vol_zscore"] < -3)).sum()
        pct = n_anomalies / len(sym_df) * 100
        ax.text(0.02, 0.95,
                f"Anomalies: {n_anomalies} ({pct:.1f}%)",
                transform=ax.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "volume_zscore_anomaly.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Chart 8: Taker Buy/Sell Ratio
# ============================================================

def chart_taker_buy_sell(df):
    """
    Analyze taker buy/sell ratio stability.
    Abnormally stable ratio indicates controlled trading (like Huobi HT).
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Taker Buy/Sell Ratio Over Time\n"
                 "Excessive stability suggests controlled/manipulated trading",
                 fontsize=14, fontweight='bold')

    for idx, symbol in enumerate(SYMBOLS):
        ax = axes[idx // 2][idx % 2]
        sym_df = df[df["symbol"] == symbol].copy().sort_values("open_time")

        ax.plot(sym_df["open_time"], sym_df["taker_buy_ratio"],
                color=COLORS[symbol], linewidth=0.8, alpha=0.8)
        ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
        ax.fill_between(sym_df["open_time"], 0.45, 0.55,
                        alpha=0.1, color='green', label='Normal range')
        ax.set_ylabel("Taker Buy Ratio")
        ax.set_title(f"{symbol.replace('USDT', '/USDT')}", fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.set_ylim(0.2, 0.8)
        ax.legend(fontsize=9)

        # Stability metric
        ratio_std = sym_df["taker_buy_ratio"].std()
        in_range = ((sym_df["taker_buy_ratio"] > 0.45) &
                    (sym_df["taker_buy_ratio"] < 0.55)).mean() * 100
        ax.text(0.02, 0.05,
                f"Std: {ratio_std:.4f}\nIn ±5% range: {in_range:.1f}%",
                transform=ax.transAxes, fontsize=10,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "taker_buy_sell_ratio.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
# Summary Statistics Table
# ============================================================

def generate_summary_stats(df, ks_results):
    """Generate summary statistics for the article."""
    stats_data = []
    for symbol in SYMBOLS:
        sym_df = df[df["symbol"] == symbol].copy()
        avg_sizes = sym_df["avg_trade_size"].dropna()
        avg_sizes = avg_sizes[avg_sizes > 0]

        # Volume-price correlation
        window = 48
        sym_df_sorted = sym_df.sort_values("open_time")
        vol_price_corr = (
            sym_df_sorted["volume_usd"]
            .rolling(window)
            .corr(sym_df_sorted["abs_price_change"])
        )

        stats_data.append({
            "Symbol": symbol.replace("USDT", "/USDT"),
            "Mean Hourly Volume (M USD)": f"${sym_df['volume_usd'].mean() / 1e6:.2f}",
            "Mean Trade Count": f"{sym_df['trades'].mean():,.0f}",
            "Mean Avg Trade Size": f"${avg_sizes.mean():,.0f}",
            "Avg Trade Size CV": f"{avg_sizes.std() / avg_sizes.mean():.2f}",
            "Vol-Price Correlation (mean)": f"{vol_price_corr.mean():.3f}",
            "Vol-Price Correlation (% negative)": f"{(vol_price_corr < 0).mean() * 100:.1f}%",
            "Taker Buy Ratio Std": f"{sym_df['taker_buy_ratio'].std():.4f}",
            "Benford KS p-value": f"{ks_results.get(symbol, {}).get('p', 'N/A'):.4f}",
        })

    stats_df = pd.DataFrame(stats_data)
    stats_path = os.path.join(DATA_DIR, "summary_statistics.csv")
    stats_df.to_csv(stats_path, index=False)
    print(f"\n  Summary statistics saved: {stats_path}")
    print(stats_df.to_string(index=False))
    return stats_df


# ============================================================
# Main
# ============================================================

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]

def main():
    print("=" * 60)
    print("Analyzing crypto market data for manipulation indicators")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    df = load_klines()
    exch_df = load_coingecko_exchanges()
    print(f"  Klines: {len(df)} rows")
    print(f"  Exchange data: {len(exch_df)} rows")

    # Generate charts
    print("\nGenerating charts...")
    chart_volume_price_correlation(df)
    chart_volume_price_impact(df)
    ks_results = chart_benford_analysis(df)
    chart_cross_exchange_divergence(exch_df)
    chart_orderbook_analysis()
    chart_trade_size_distribution(df)
    chart_volume_anomaly(df)
    chart_taker_buy_sell(df)

    # Summary stats
    print("\nGenerating summary statistics...")
    generate_summary_stats(df, ks_results)

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(f"Charts saved to: {IMG_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
