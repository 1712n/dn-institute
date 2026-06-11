"""
Reproduction script for FTT/FTX collapse market analysis.
Requires: requests, numpy, pandas, matplotlib, scipy
Data: Binance public REST API (no API key required)
"""
import requests, json, time, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.gridspec as gridspec
from scipy import stats

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
all_candles = []
start = 1667260800000  # 2022-11-01 00:00 UTC
end   = 1668470400000  # 2022-11-15 00:00 UTC

print("Fetching FTT/USDT 5m candles from Binance...")
while start < end:
    resp = requests.get("https://api.binance.com/api/v3/klines", params={
        "symbol": "FTTUSDT", "interval": "5m",
        "startTime": start, "endTime": end, "limit": 1000
    }, timeout=20)
    data = resp.json()
    if not data: break
    all_candles.extend(data)
    start = data[-1][0] + 300000
    time.sleep(0.1)

cols = ['open_time','open','high','low','close','volume','close_time','quote_vol',
        'trades','taker_buy_base','taker_buy_quote','ignore']
df = pd.DataFrame(all_candles, columns=cols)
for c in ['open','high','low','close','volume','quote_vol','trades','taker_buy_base','taker_buy_quote']:
    df[c] = df[c].astype(float)
df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
df['taker_buy_ratio'] = df['taker_buy_quote'] / df['quote_vol'].replace(0, np.nan)

collapse_start = pd.Timestamp('2022-11-06 00:00:00')
df_pre = df[df['open_time'] < collapse_start]
df_col = df[df['open_time'] >= collapse_start]

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
    return counts/len(digits), chi2, p

col_bf_qv, col_chi2_qv, col_p_qv = benford_test(df_col['quote_vol'].values)
ks_stat, ks_p = stats.ks_2samp(df_pre['quote_vol'].values, df_col['quote_vol'].values)

print(f"Vol ratio: {df_col['quote_vol'].mean()/df_pre['quote_vol'].mean():.1f}x")
print(f"KS: {ks_stat:.4f}, p={ks_p:.2e}")
print(f"Collapse Benford (vols): chi2={col_chi2_qv:.1f}, p={col_p_qv:.3f}")

fig = plt.figure(figsize=(16,12))
gs = gridspec.GridSpec(3,2,figure=fig,hspace=0.45,wspace=0.35)
fig.suptitle("FTT/USDT — FTX Collapse Volume Anomaly Analysis (Nov 2022)", fontsize=15, fontweight='bold')
x = np.array(range(1,10)); w = 0.35

ax1 = fig.add_subplot(gs[0,0:2])
hourly = df.resample('h', on='open_time')['quote_vol'].sum()/1e6
colors = ['#F44336' if t >= collapse_start else '#2196F3' for t in hourly.index]
ax1.bar(range(len(hourly)), hourly.values, color=colors, alpha=0.85, width=1.0)
cidx = next(i for i,t in enumerate(hourly.index) if t >= collapse_start)
ax1.axvline(cidx, color='black', linestyle='--', linewidth=1.5, label='Nov 6: CZ tweet')
ax1.set_ylabel('USD Volume (Millions)'); ax1.set_title('Hourly Volume'); ax1.legend(); ax1.grid(axis='y',alpha=0.3)
tl=list(range(0,len(hourly),24)); ax1.set_xticks(tl)
ax1.set_xticklabels([str(hourly.index[i].date()) for i in tl if i<len(hourly)], rotation=45, ha='right', fontsize=8)

ax2 = fig.add_subplot(gs[1,0])
ax2.bar(x-w/2, col_bf_qv, w, label='Collapse Observed', color='#F44336', alpha=0.8)
ax2.bar(x+w/2, benford_expected, w, label='Benford Expected', color='#FF9800', alpha=0.8)
ax2.set_title(f"Benford — Dollar Volumes\n(χ²={col_chi2_qv:.1f}, p={col_p_qv:.3f})")
ax2.set_xticks(x); ax2.legend(fontsize=9); ax2.grid(axis='y',alpha=0.3)

ax3 = fig.add_subplot(gs[1,1])
hr = df.resample('h', on='open_time')['taker_buy_ratio'].mean()
c2 = ['#F44336' if t >= collapse_start else '#2196F3' for t in hr.index]
ax3.bar(range(len(hr)), hr.values*100, color=c2, alpha=0.8, width=1.0)
ax3.axhline(50, color='black', linestyle='--', alpha=0.5)
ax3.set_ylabel('Taker Buy %'); ax3.set_title('Buy/Sell Ratio'); ax3.set_ylim(0,100); ax3.grid(axis='y',alpha=0.3)

ax4 = fig.add_subplot(gs[2,0:2])
ax4.semilogy(df['open_time'], df['close'], color='#E91E63', linewidth=1)
ax4.axvline(collapse_start, color='black', linestyle='--', linewidth=1.5, label='Nov 6: CZ tweet')
ax4.axvline(pd.Timestamp('2022-11-08'), color='red', linestyle=':', linewidth=1.5, label='Nov 8: withdrawals halted')
ax4.set_ylabel('FTT Price (log)'); ax4.set_title('FTT/USDT Price (log scale)')
ax4.legend(); ax4.grid(alpha=0.3)

plt.savefig(f"{OUTPUT_DIR}/ftt-collapse-analysis.png", dpi=150, bbox_inches='tight')
print(f"Chart saved: {OUTPUT_DIR}/ftt-collapse-analysis.png")
