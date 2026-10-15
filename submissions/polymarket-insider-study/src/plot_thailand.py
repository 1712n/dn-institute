import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1] / 'cases/thailand'
summary = json.loads((ROOT / 'artifacts/focus_summary.json').read_text())
with (ROOT / 'artifacts/focus_daily_trades.csv').open(encoding='utf-8') as f:
    rows = [r for r in csv.DictReader(f) if 'bhumjaithai' in r['market_slug']]
by_date = {r['date_utc']: float(r['notional_usdc']) for r in rows}
start = datetime(2026, 1, 8, tzinfo=timezone.utc)
dates = [start + timedelta(days=d) for d in range(32)]
values = [by_date.get(d.strftime('%Y-%m-%d'), 0) / 1000 for d in dates]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig, ax = plt.subplots(figsize=(11, 4.6), dpi=170)
fig.patch.set_facecolor('#ffffff')
ax.bar(dates, values, width=.76, color=['#23867d' if d.day <= 8 and d.month == 2 and d.day >= 5 else '#a9b8c9' for d in dates])
ax.set_title('Bhumjaithai YES purchases before election-day polling', loc='left', fontweight='bold', fontsize=14, pad=36)
ax.text(0, 1.05, 'Wallet 0x1cfc6f...5b8e0 | $124,136.47 total | 86.36% bought in the final 72 hours', transform=ax.transAxes, color='#46556b', fontsize=10)
ax.set_ylabel('USDC spent, thousands')
ax.set_ylim(0, 62)
ax.set_axisbelow(True)
ax.grid(axis='y', color='#e5e9ee', linewidth=.7)
for name in ['top', 'right', 'left']:
    ax.spines[name].set_visible(False)
ax.spines['bottom'].set_color('#ccd2dc')
ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.tick_params(axis='both', length=0, pad=8)
for d, v in zip(dates, values):
    if v > 10:
        ax.text(d, v + 1.3, f'${v:.1f}k', ha='center', fontsize=10, color='#155b54')
fig.text(.08, .025, 'UTC dates. February 8 includes only trades before 00:30 UTC. Activity history includes maker and taker trades.', fontsize=9, color='#536276')
fig.subplots_adjust(left=.08, right=.98, top=.77, bottom=.15)
(ROOT / 'figures').mkdir(exist_ok=True)
fig.savefig(ROOT / 'figures/daily_buying.png', facecolor='white', metadata={'Software':'Matplotlib'})
plt.close(fig)
