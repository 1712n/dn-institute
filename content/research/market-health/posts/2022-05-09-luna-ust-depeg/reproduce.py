"""
Reproduction script for LUNA/UST depeg market anomaly analysis.
Requires: requests, numpy, pandas, matplotlib, scipy
Data: Binance public REST API (no API key required)
"""
import requests, json, time, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fetch 5-minute OHLCV for LUNA/USDT: May 1 – May 13, 2022
all_candles = []
start = 1651363200000   # 2022-05-01 00:00 UTC
end   = 1652486400000   # 2022-05-14 00:00 UTC

print("Fetching LUNA/USDT 5m candles from Binance...")
while start < end:
    resp = requests.get("https://api.binance.com/api/v3/klines", params={
        "symbol": "LUNAUSDT", "interval": "5m",
        "startTime": start, "endTime": end, "limit": 1000
    }, timeout=20)
    data = resp.json()
    if not data:
        break
    all_candles.extend(data)
    start = data[-1][0] + 300000
    time.sleep(0.1)
print(f"Total candles: {len(all_candles)}")

cols = ['open_time','open','high','low','close','volume','close_time','quote_vol',
        'trades','taker_buy_base','taker_buy_quote','ignore']
df = pd.DataFrame(all_candles, columns=cols)
for c in ['open','high','low','close','volume','quote_vol','trades','taker_buy_base','taker_buy_quote']:
    df[c] = df[c].astype(float)
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
df['taker_buy_ratio'] = df['taker_buy_quote'] / df['quote_vol'].replace(0, np.nan)

crash_start = pd.Timestamp('2022-05-09 00:00:00')
df_pre   = df[df['open_time'] < crash_start].copy()
df_crash = df[df['open_time'] >= crash_start].copy()

benford_expected = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

def benford_test(series):
    digits = []
    for val in series:
        if val <= 0: continue
        s = f"{val:.10f}".lstrip('0').replace('.','').lstrip('0')
        if s: digits.append(int(s[0]))
    digits = [d for d in digits if 1 <= d <= 9]
    counts = np.array([digits.count(d) for d in range(1,10)])
    chi2, p = stats.chisquare(counts, f_exp=benford_expected * len(digits))
    obs = counts / len(digits)
    return obs, chi2, p

pre_bf_tc,  pre_chi2_tc,  _  = benford_test(df_pre['trades'].values)
crash_bf_tc, crash_chi2_tc, crash_p_tc = benford_test(df_crash['trades'].values)
pre_bf_qv,  pre_chi2_qv,  _  = benford_test(df_pre['quote_vol'].values)
crash_bf_qv, crash_chi2_qv, crash_p_qv = benford_test(df_crash['quote_vol'].values)

ks_stat, ks_p = stats.ks_2samp(df_pre['quote_vol'].values, df_crash['quote_vol'].values)
pre_corr   = np.corrcoef(df_pre['trades'].values,   df_pre['quote_vol'].values)[0,1]
crash_corr = np.corrcoef(df_crash['trades'].values, df_crash['quote_vol'].values)[0,1]

print(f"Volume ratio: {df_crash['quote_vol'].mean()/df_pre['quote_vol'].mean():.1f}x")
print(f"KS stat: {ks_stat:.4f}, p={ks_p:.2e}")
print(f"Crash Benford (vols): chi2={crash_chi2_qv:.1f}, p={crash_p_qv:.2e}")
print(f"Pre corr: {pre_corr:.4f}, Crash corr: {crash_corr:.4f}")

# Chart
fig = plt.figure(figsize=(16, 12))
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)
fig.suptitle("LUNA/USDT May 2022 Collapse — Market Anomaly Analysis", fontsize=15, fontweight='bold')

digits_range = range(1, 10)
x = np.array(list(digits_range))
w = 0.35

ax1 = fig.add_subplot(gs[0, 0:2])
hourly = df.resample('h', on='open_time')['quote_vol'].sum() / 1e6
colors = ['#F44336' if t >= crash_start else '#2196F3' for t in hourly.index]
ax1.bar(range(len(hourly)), hourly.values, color=colors, alpha=0.85, width=1.0)
crash_idx = next(i for i, t in enumerate(hourly.index) if t >= crash_start)
ax1.axvline(crash_idx, color='black', linestyle='--', linewidth=1.5, label='Crash starts May 9')
ax1.set_ylabel('USD Volume (Millions)')
ax1.set_title('Hourly Volume: Pre-crash (blue) vs Crash (red)')
ax1.legend(); ax1.grid(axis='y', alpha=0.3)
tl = list(range(0, len(hourly), 24))
ax1.set_xticks(tl)
ax1.set_xticklabels([str(hourly.index[i].date()) for i in tl if i < len(hourly)], rotation=45, ha='right', fontsize=8)

ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(x - w/2, crash_bf_qv, w, label='Crash Observed', color='#F44336', alpha=0.8)
ax2.bar(x + w/2, benford_expected, w, label='Benford Expected', color='#FF9800', alpha=0.8)
ax2.set_xlabel('First Digit'); ax2.set_ylabel('Relative Frequency')
ax2.set_title(f"Benford — Dollar Volumes (Crash)\n(χ²={crash_chi2_qv:.1f}, p={crash_p_qv:.1e})")
ax2.set_xticks(x); ax2.legend(fontsize=9); ax2.grid(axis='y', alpha=0.3)

ax3 = fig.add_subplot(gs[1, 1])
hourly_r = df.resample('h', on='open_time')['taker_buy_ratio'].mean()
colors2  = ['#F44336' if t >= crash_start else '#2196F3' for t in hourly_r.index]
ax3.bar(range(len(hourly_r)), hourly_r.values * 100, color=colors2, alpha=0.8, width=1.0)
ax3.axhline(50, color='black', linestyle='--', alpha=0.5)
ax3.set_ylabel('Taker Buy %'); ax3.set_title('Hourly Buy/Sell Ratio')
ax3.set_ylim(0, 100); ax3.grid(axis='y', alpha=0.3)

ax4 = fig.add_subplot(gs[2, 0:2])
ax4.semilogy(df['open_time'], df['close'], color='#9C27B0', linewidth=1)
ax4.axvline(crash_start, color='red', linestyle='--', linewidth=1.5, label='May 9')
ax4.set_ylabel('LUNA Price USD (log)'); ax4.set_title('LUNA/USDT Price (log scale)')
ax4.legend(); ax4.grid(alpha=0.3)

plt.savefig(f"{OUTPUT_DIR}/luna-collapse-analysis.png", dpi=150, bbox_inches='tight')
print(f"Chart saved to {OUTPUT_DIR}/luna-collapse-analysis.png")
