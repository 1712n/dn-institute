"""
TRUMP Memecoin Launch Market Health Analysis - v2
Using 5-minute OHLCV data for statistical analysis
"""
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from scipy import stats
import json, time, os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCH_START_MS = 1737275400000  # Jan 19, 2025 08:30 UTC (Binance listing time)

def fetch_klines_all(symbol, interval, start_ms, end_ms, base="https://api.binance.com"):
    url = f"{base}/api/v3/klines"
    all_data = []
    cur = start_ms
    while cur < end_ms:
        r = requests.get(url, params={"symbol": symbol, "interval": interval,
                                       "startTime": cur, "endTime": min(cur + 500*300000, end_ms),
                                       "limit": 500}, timeout=20)
        if r.status_code != 200 or not r.json():
            break
        d = r.json()
        all_data.extend(d)
        cur = int(d[-1][0]) + 300000
        time.sleep(0.15)
    return all_data

print("Fetching 5-minute candles (first 14 days)...")
end_ms = LAUNCH_START_MS + 14 * 86400000

raw = fetch_klines_all("TRUMPUSDT", "5m", LAUNCH_START_MS, end_ms)
print(f"Got {len(raw)} five-minute candles")

cols = ['open_time','open','high','low','close','volume','close_time','quote_vol',
        'trades','taker_buy_base','taker_buy_quote','ignore']
df = pd.DataFrame(raw, columns=cols)
for c in ['open','high','low','close','volume','quote_vol','trades','taker_buy_base','taker_buy_quote']:
    df[c] = df[c].astype(float)
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)

print(f"Range: {df['open_time'].min()} → {df['open_time'].max()}")
print(f"Peak 5m volume: ${df['quote_vol'].max()/1e6:.1f}M at {df.loc[df['quote_vol'].idxmax(), 'open_time']}")

# === SPLIT: Launch (Jan 19 08:30 – Jan 21 00:00 UTC) vs Stabilized ===
boundary = pd.Timestamp('2025-01-21 00:00:00', tz='UTC')
launch = df[df['open_time'] < boundary].copy()
stable = df[df['open_time'] >= boundary].copy()
print(f"\nLaunch (Jan 19 08:30 – Jan 21 00:00 UTC):   {len(launch)} candles, avg 5m vol: ${launch['quote_vol'].mean()/1e3:.1f}K, total: ${launch['quote_vol'].sum()/1e9:.2f}B")
print(f"Stable  (days3-14):{len(stable)} candles, avg 5m vol: ${stable['quote_vol'].mean()/1e3:.1f}K, total: ${stable['quote_vol'].sum()/1e9:.2f}B")
vol_ratio = launch['quote_vol'].mean() / stable['quote_vol'].mean()
print(f"Volume ratio (launch/stable): {vol_ratio:.1f}x")

# === BUY/SELL RATIO ===
launch_buy_r = launch['taker_buy_quote'].sum() / launch['quote_vol'].sum()
stable_buy_r = stable['taker_buy_quote'].sum() / stable['quote_vol'].sum()
print(f"\nBuy ratio - Launch: {launch_buy_r:.4f} ({launch_buy_r*100:.1f}%)")
print(f"Buy ratio - Stable: {stable_buy_r:.4f} ({stable_buy_r*100:.1f}%)")

# Buy ratio variance (should fluctuate more in organic markets)
launch_buy_per_bar = launch['taker_buy_quote'] / launch['quote_vol'].replace(0, np.nan)
stable_buy_per_bar = stable['taker_buy_quote'] / stable['quote_vol'].replace(0, np.nan)
print(f"Buy ratio std - Launch: {launch_buy_per_bar.std():.4f}")
print(f"Buy ratio std - Stable: {stable_buy_per_bar.std():.4f}")

# === BENFORD'S LAW on 5-min trade COUNTS ===
benford_expected = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

def benford_test(series, name):
    digits = []
    for v in series:
        s = str(int(max(1, v)))
        if s[0] in '123456789':
            digits.append(int(s[0]))
    if len(digits) < 50:
        return None, None, None, None
    counts = np.array([digits.count(d) for d in range(1, 10)])
    n = len(digits)
    obs = counts / n
    chi2, p = stats.chisquare(counts, f_exp=benford_expected * n)
    ks = np.max(np.abs(np.cumsum(obs) - np.cumsum(benford_expected)))
    print(f"\n{name} Benford (N={n}): χ²={chi2:.2f}, p={p:.4f}, KS={ks:.4f}")
    return obs, chi2, p, ks

# Benford on trade counts per 5-minute bar
l_obs, l_chi2, l_p, l_ks = benford_test(launch['trades'].values, "Launch trade counts")
s_obs, s_chi2, s_p, s_ks = benford_test(stable['trades'].values, "Stable trade counts")

# Benford on 5-min dollar volumes
l_vol_obs, l_v_chi2, l_v_p, l_v_ks = benford_test(launch['quote_vol'].values, "Launch volumes")
s_vol_obs, s_v_chi2, s_v_p, s_v_ks = benford_test(stable['quote_vol'].values, "Stable volumes")

# === TRADE COUNT vs VOLUME CORRELATION ===
# In organic markets, trade count and volume should be highly correlated
l_corr = launch['trades'].corr(launch['quote_vol'])
s_corr = stable['trades'].corr(stable['quote_vol'])
print(f"\nTrade count/volume correlation:")
print(f"  Launch: {l_corr:.4f}")
print(f"  Stable: {s_corr:.4f}")

# === PRICE IMPACT ANALYSIS ===
# In wash trading, large volume shouldn't move the price much
df['price_change_pct'] = df['close'].pct_change().abs() * 100
df['vol_bucket'] = pd.qcut(df['quote_vol'].rank(method='first'), 5, labels=['Q1','Q2','Q3','Q4','Q5'])
price_impact = df.groupby('vol_bucket', observed=True)['price_change_pct'].median()
print(f"\nMedian price change by volume quintile:")
for q, v in price_impact.items():
    print(f"  {q}: {v:.4f}%")

# === GENERATE COMPREHENSIVE CHARTS ===
print("\n=== Generating charts ===")
fig = plt.figure(figsize=(20, 18))
fig.suptitle("TRUMP/USDT (Binance Spot): Market Manipulation Analysis at Launch\nJanuary 19–February 2, 2025",
             fontsize=15, fontweight='bold', y=0.99)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.38)

digits = np.arange(1, 10)
w = 0.35

# 1. Hourly volume - full timeline
ax1 = fig.add_subplot(gs[0, :])
hourly = df.resample('1h', on='open_time')['quote_vol'].sum()
colors = ['#E53935' if t < pd.Timestamp('2025-01-21') else '#1976D2'
          for t in hourly.index]
ax1.bar(hourly.index, hourly.values/1e6, color=colors, alpha=0.85,
        width=pd.Timedelta(minutes=55))
ax1.axvline(pd.Timestamp('2025-01-21'), color='black', linestyle='--',
            linewidth=2, label='39.5h boundary (Jan 21 00:00 UTC)')
peak_t = hourly.idxmax()
ax1.annotate(f"${hourly.max()/1e6:.0f}M",
    xy=(peak_t, hourly.max()/1e6), xytext=(5, 5),
    textcoords='offset points', fontsize=10, color='darkred',
    fontweight='bold', arrowprops=dict(arrowstyle='->', color='darkred'))
ax1.set_title('Hourly Volume (Red=Launch 0–39.5h, Blue=Stabilized)', fontsize=11)
ax1.set_ylabel('Volume (USD Millions)')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.xaxis.set_major_locator(mdates.DayLocator())
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
ax1.legend(); ax1.grid(axis='y', alpha=0.3)
ax1.text(0.02, 0.92, f"Launch avg: ${launch['quote_vol'].sum()/39.5/1e6:.0f}M/hr | Stable avg: ${stable['quote_vol'].sum()/len(stable)*12/1e6:.0f}M/hr | Ratio: {vol_ratio:.1f}x",
    transform=ax1.transAxes, fontsize=9, color='darkred',
    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 2. Benford on trade counts - launch
ax2 = fig.add_subplot(gs[1, 0])
if l_obs is not None:
    ax2.bar(digits - w/2, l_obs, w, color='#E53935', alpha=0.85, label='Observed')
    ax2.bar(digits + w/2, benford_expected, w, color='#607D8B', alpha=0.85, label='Expected')
ax2.set_title(f"Benford (Trade Counts): Launch\nχ²={l_chi2:.1f}, p={l_p:.3f}" if l_chi2 else "Benford: Launch")
ax2.set_xticks(digits); ax2.legend(fontsize=8); ax2.grid(axis='y', alpha=0.3)
ax2.set_xlabel('First Digit'); ax2.set_ylabel('Relative Frequency')

# 3. Benford on trade counts - stable
ax3 = fig.add_subplot(gs[1, 1])
if s_obs is not None:
    ax3.bar(digits - w/2, s_obs, w, color='#1976D2', alpha=0.85, label='Observed')
    ax3.bar(digits + w/2, benford_expected, w, color='#607D8B', alpha=0.85, label='Expected')
ax3.set_title(f"Benford (Trade Counts): Stabilized\nχ²={s_chi2:.1f}, p={s_p:.3f}" if s_chi2 else "Benford: Stable")
ax3.set_xticks(digits); ax3.legend(fontsize=8); ax3.grid(axis='y', alpha=0.3)
ax3.set_xlabel('First Digit'); ax3.set_ylabel('Relative Frequency')

# 4. Buy/Sell ratio over time
ax4 = fig.add_subplot(gs[1, 2])
rolling_buy = (df['taker_buy_quote'] / df['quote_vol'].replace(0, np.nan)).rolling(12).mean()
hours = (df['open_time'] - df['open_time'].iloc[0]).dt.total_seconds() / 3600
ax4.plot(hours, rolling_buy * 100, color='#2E7D32', linewidth=1.5, alpha=0.8)
ax4.axhline(50, color='black', linestyle='--', alpha=0.5, linewidth=1, label='50% (neutral)')
ax4.axvline(39.5, color='red', linestyle='--', alpha=0.7, label='39.5h boundary (Jan 21 00:00 UTC)')
ax4.set_title(f"Buy Volume % (rolling 1h avg)\nLaunch: {launch_buy_r*100:.1f}% | Stable: {stable_buy_r*100:.1f}%")
ax4.set_xlabel('Hours Since Launch'); ax4.set_ylabel('Buy Volume %')
ax4.set_ylim(30, 70); ax4.legend(fontsize=8); ax4.grid(alpha=0.3)

# 5. Volume distribution (launch vs stable)
ax5 = fig.add_subplot(gs[2, 0])
log_launch = np.log10(launch['quote_vol'].values[launch['quote_vol'].values > 0])
log_stable = np.log10(stable['quote_vol'].values[stable['quote_vol'].values > 0])
ax5.hist(log_launch, bins=40, alpha=0.7, label='Launch (0–39.5h)', color='#E53935', density=True)
ax5.hist(log_stable, bins=40, alpha=0.7, label='Stabilized', color='#1976D2', density=True)
ks_stat, ks_p = stats.ks_2samp(log_launch, log_stable)
ax5.set_title(f"5m Volume Distribution\nKS test: stat={ks_stat:.3f}, p={ks_p:.2e}")
ax5.set_xlabel('log₁₀(5m Volume USD)'); ax5.set_ylabel('Density')
ax5.legend(fontsize=8); ax5.grid(alpha=0.3)

# 6. Price impact by volume quintile
ax6 = fig.add_subplot(gs[2, 1])
quintile_labels = [f'Q{i+1}' for i in range(5)]
bar_colors = ['#FFCDD2','#EF9A9A','#E57373','#EF5350','#E53935']
ax6.bar(quintile_labels, price_impact.values, color=bar_colors, alpha=0.85)
ax6.set_title("Median Price Impact by Volume Quintile\n(Low→High Volume)")
ax6.set_xlabel('Volume Quintile (Q1=lowest)'); ax6.set_ylabel('Median |Price Change| %')
ax6.grid(axis='y', alpha=0.3)
for i, (q, v) in enumerate(price_impact.items()):
    ax6.text(i, v + 0.0001, f'{v:.4f}%', ha='center', va='bottom', fontsize=9)

# 7. Trade count vs volume scatter
ax7 = fig.add_subplot(gs[2, 2])
launch_sample = launch.sample(min(500, len(launch)))
stable_sample = stable.sample(min(500, len(stable)))
ax7.scatter(np.log10(launch_sample['trades'].values + 1),
            np.log10(launch_sample['quote_vol'].values + 1),
            alpha=0.4, s=10, color='#E53935', label=f'Launch (r={l_corr:.3f})')
ax7.scatter(np.log10(stable_sample['trades'].values + 1),
            np.log10(stable_sample['quote_vol'].values + 1),
            alpha=0.4, s=10, color='#1976D2', label=f'Stable (r={s_corr:.3f})')
ax7.set_title("Trade Count vs Volume Correlation\n(Higher r = more consistent per-trade size)")
ax7.set_xlabel('log₁₀(Trade Count)'); ax7.set_ylabel('log₁₀(Volume USD)')
ax7.legend(fontsize=8); ax7.grid(alpha=0.3)

plt.savefig(f"{OUTPUT_DIR}/trump-manipulation-analysis.png", dpi=150, bbox_inches='tight')
print(f"Saved: {OUTPUT_DIR}/trump-manipulation-analysis.png")

# Also generate a second focused chart
fig2, axes = plt.subplots(1, 2, figsize=(14, 5))
fig2.suptitle("TRUMP Token: Volume vs Price Dynamics — Evidence of Artificial Inflation", fontsize=12, fontweight='bold')

# Price timeline
price_hourly = df.resample('1h', on='open_time')['close'].last()
ax_p = axes[0]
ax_p.plot(price_hourly.index, price_hourly.values, color='#FF9800', linewidth=2)
ax_p.axvline(pd.Timestamp('2025-01-21'), color='red', linestyle='--', alpha=0.7, label='39.5h boundary (Jan 21 00:00 UTC)')
ax_p.set_title('TRUMP Price (USDT) — First 14 Days')
ax_p.set_ylabel('Price (USDT)')
ax_p.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax_p.xaxis.set_major_locator(mdates.DayLocator())
plt.setp(ax_p.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
ax_p.legend(); ax_p.grid(alpha=0.3)

# Volume vs price change scatter
vol_pct = df['quote_vol'] / 1e6
price_chg = df['close'].pct_change().abs() * 100
valid = (vol_pct > 0) & (price_chg < price_chg.quantile(0.99))
launch_mask = (df['open_time'] < boundary) & valid
stable_mask = (df['open_time'] >= boundary) & valid
axes[1].scatter(vol_pct[launch_mask], price_chg[launch_mask], alpha=0.3, s=8,
                color='#E53935', label='Launch')
axes[1].scatter(vol_pct[stable_mask], price_chg[stable_mask], alpha=0.3, s=8,
                color='#1976D2', label='Stable')
axes[1].set_title('Volume vs Price Impact per 5-min Bar\n(Wash trades: high volume, low impact)')
axes[1].set_xlabel('5m Volume (USD Millions)'); axes[1].set_ylabel('|Price Change| %')
axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)
axes[1].set_xlim(0, vol_pct.quantile(0.98))

fig2.tight_layout()
fig2.savefig(f"{OUTPUT_DIR}/trump-price-volume.png", dpi=150, bbox_inches='tight')
print(f"Saved: {OUTPUT_DIR}/trump-price-volume.png")

stats_out = {
    'launch_total_volume_B': float(launch['quote_vol'].sum()/1e9),
    'stable_total_volume_B': float(stable['quote_vol'].sum()/1e9),
    'vol_ratio': float(vol_ratio),
    'launch_buy_ratio': float(launch_buy_r),
    'stable_buy_ratio': float(stable_buy_r),
    'launch_buy_ratio_std': float(launch_buy_per_bar.std()),
    'stable_buy_ratio_std': float(stable_buy_per_bar.std()),
    'launch_benford_chi2': float(l_chi2) if l_chi2 else None,
    'launch_benford_p': float(l_p) if l_p else None,
    'stable_benford_chi2': float(s_chi2) if s_chi2 else None,
    'stable_benford_p': float(s_p) if s_p else None,
    'ks_volume_dist': float(ks_stat),
    'ks_volume_p': float(ks_p),
    'trade_vol_corr_launch': float(l_corr),
    'trade_vol_corr_stable': float(s_corr),
    'peak_hourly_vol_M': float(hourly.max()/1e6),
    'peak_hour': str(hourly.idxmax()),
}
with open(f"{OUTPUT_DIR}/trump_stats_v2.json", 'w') as f:
    json.dump(stats_out, f, indent=2)

print("\n=== Complete! ===")
print(json.dumps(stats_out, indent=2))
