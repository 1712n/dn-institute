"""
Reproduction script for XRP/USDT SEC ruling surge analysis (July 2023).
Requires: requests, numpy, pandas, matplotlib, scipy
Data: Binance public REST API (no API key required)
"""
import requests, time, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fetch XRP/USDT 5m: July 9 – July 20, 2023
all_candles = []
start = 1688860800000   # 2023-07-09 00:00 UTC
end   = 1689811200000   # 2023-07-20 00:00 UTC

print("Fetching XRPUSDT 5m candles from Binance...")
while start < end:
    resp = requests.get("https://api.binance.com/api/v3/klines", params={
        "symbol": "XRPUSDT", "interval": "5m",
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
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
df['taker_buy_ratio'] = df['taker_buy_quote'] / df['quote_vol'].replace(0, np.nan)

surge_start = pd.Timestamp('2023-07-13 00:00:00', tz='UTC')
df_pre   = df[df['open_time'] < surge_start].copy()
df_surge = df[df['open_time'] >= surge_start].copy()
df_acute = df_surge[df_surge['open_time'] < pd.Timestamp('2023-07-14 00:00:00', tz='UTC')].copy()

benford_expected = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

def benford_test(series):
    digits = []
    for val in series:
        if val <= 0: continue
        s = f"{val:.10f}".lstrip('0').replace('.','').lstrip('0')
        if s: digits.append(int(s[0]))
    digits = [d for d in digits if 1 <= d <= 9]
    n = len(digits)
    counts = np.array([digits.count(d) for d in range(1,10)])
    chi2, p = stats.chisquare(counts, f_exp=benford_expected * n)
    obs = counts / n
    return obs, chi2, p

pre_bf_tc,  pre_chi2_tc,   pre_p_tc   = benford_test(df_pre['trades'].values)
surge_bf_tc, surge_chi2_tc, surge_p_tc = benford_test(df_surge['trades'].values)
pre_bf_qv,  pre_chi2_qv,   pre_p_qv   = benford_test(df_pre['quote_vol'].values)
surge_bf_qv, surge_chi2_qv, surge_p_qv = benford_test(df_surge['quote_vol'].values)

ks_stat, ks_p = stats.ks_2samp(df_pre['quote_vol'].values, df_surge['quote_vol'].values)
pre_corr   = np.corrcoef(df_pre['trades'].values,   df_pre['quote_vol'].values)[0,1]
surge_corr = np.corrcoef(df_surge['trades'].values, df_surge['quote_vol'].values)[0,1]

print(f"Volume ratio (acute):  {df_acute['quote_vol'].mean()/df_pre['quote_vol'].mean():.1f}x")
print(f"Volume ratio (7-day):  {df_surge['quote_vol'].mean()/df_pre['quote_vol'].mean():.1f}x")
print(f"Pre  buy ratio: {df_pre['taker_buy_ratio'].mean():.3f}, std: {df_pre['taker_buy_ratio'].std():.3f}")
print(f"Surge buy ratio: {df_surge['taker_buy_ratio'].mean():.3f}, std: {df_surge['taker_buy_ratio'].std():.3f}")
print(f"KS stat: {ks_stat:.4f}, p={ks_p:.2e}")
print(f"Correlations — Pre: {pre_corr:.4f}, Surge: {surge_corr:.4f}")
print(f"Benford Surge trade counts: chi2={surge_chi2_tc:.1f}, p={surge_p_tc:.3f}")
print(f"Benford Surge volumes:      chi2={surge_chi2_qv:.1f}, p={surge_p_qv:.3f}")

# --- Chart ---
fig = plt.figure(figsize=(16, 12))
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)
fig.suptitle("XRP/USDT July 2023 SEC Ruling Surge — Market Microstructure Analysis",
             fontsize=14, fontweight='bold')

digits_range = range(1, 10)
x = np.array(list(digits_range))
w = 0.35

# Panel 1: hourly volume
ax1 = fig.add_subplot(gs[0, 0:2])
hourly = df.resample('h', on='open_time')['quote_vol'].sum() / 1e6
colors = ['#F44336' if t >= surge_start else '#2196F3' for t in hourly.index]
ax1.bar(range(len(hourly)), hourly.values, color=colors, alpha=0.85, width=1.0)
surge_idx = next(i for i, t in enumerate(hourly.index) if t >= surge_start)
ax1.axvline(surge_idx, color='black', linestyle='--', linewidth=1.5, label='Ruling: Jul 13 00:00 UTC')
ax1.set_ylabel('USD Volume (Millions)')
ax1.set_title('Hourly Volume: Pre-ruling (blue) vs Surge (red)')
ax1.legend(); ax1.grid(axis='y', alpha=0.3)
tl = list(range(0, len(hourly), 24))
ax1.set_xticks(tl)
ax1.set_xticklabels([str(hourly.index[i].date()) for i in tl if i < len(hourly)],
                    rotation=45, ha='right', fontsize=8)

# Panel 2: Benford surge volumes
ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(x - w/2, surge_bf_qv, w, label='Surge Observed', color='#F44336', alpha=0.8)
ax2.bar(x + w/2, benford_expected, w, label='Benford Expected', color='#FF9800', alpha=0.8)
ax2.set_xlabel('First Digit'); ax2.set_ylabel('Relative Frequency')
ax2.set_title(f"Benford — Dollar Volumes (Surge)\n(χ²={surge_chi2_qv:.1f}, p={surge_p_qv:.1e})")
ax2.set_xticks(x); ax2.legend(fontsize=9); ax2.grid(axis='y', alpha=0.3)

# Panel 3: buy/sell ratio over time
ax3 = fig.add_subplot(gs[1, 1])
hourly_r = df.resample('h', on='open_time')['taker_buy_ratio'].mean()
colors2  = ['#F44336' if t >= surge_start else '#2196F3' for t in hourly_r.index]
ax3.bar(range(len(hourly_r)), hourly_r.values * 100, color=colors2, alpha=0.8, width=1.0)
ax3.axhline(50, color='black', linestyle='--', alpha=0.5)
ax3.set_ylabel('Taker Buy %'); ax3.set_title('Hourly Buy/Sell Ratio')
ax3.set_ylim(0, 100); ax3.grid(axis='y', alpha=0.3)

# Panel 4: price
ax4 = fig.add_subplot(gs[2, 0:2])
ax4.plot(df['open_time'], df['close'], color='#9C27B0', linewidth=1)
ax4.axvline(surge_start, color='red', linestyle='--', linewidth=1.5, label='Jul 13: SEC ruling')
ax4.set_ylabel('XRP Price USD'); ax4.set_title('XRP/USDT Price')
ax4.legend(); ax4.grid(alpha=0.3)

plt.savefig(f"{OUTPUT_DIR}/xrp-ruling-analysis.png", dpi=150, bbox_inches='tight')
print(f"Chart saved to {OUTPUT_DIR}/xrp-ruling-analysis.png")
