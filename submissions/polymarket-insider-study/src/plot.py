"""Optional static research figures. pip install matplotlib==3.11.2"""
import csv
from datetime import datetime, timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collect import ROOT, read_json, epoch


def table(name):
    with (ROOT / 'artifacts' / name).open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def dt(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


def main():
    out = ROOT / 'figures'
    out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.labelcolor': '#283c4b', 'text.color': '#152c3b',
                         'axes.titleweight': 'bold', 'savefig.facecolor': 'white'})
    ranks = [r for r in table('ranking.csv') if r['eligible'] == 'True']
    fig, ax = plt.subplots(figsize=(11, 6.5), layout='constrained')
    left = [0.] * len(ranks)
    labels = [f"{r['rank']}. {r['wallet'][:8]}…{r['wallet'][-5:]}" for r in ranks]
    for key, title, color in [('size', 'Purchase size (30)', '#173a55'), ('recency', 'Recent buying (25)', '#227b8a'),
                              ('direction', 'Mostly YES buying (20)', '#68b0ab'), ('surprise', 'Low entry price (25)', '#e4ba64')]:
        values = [float(r[key + '_points']) for r in ranks]
        ax.barh(labels, values, left=left, color=color, label=title, height=.64)
        left = [a+b for a, b in zip(left, values)]
    for i, r in enumerate(ranks):
        ax.text(float(r['score']) + .8, i, f"{float(r['score']):.2f}", va='center', fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, 108)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel('Score out of 100 (not a probability)')
    ax.set_title('Eight wallets met the $500 minimum', loc='left', pad=65)
    ax.xaxis.grid(True, alpha=.14)
    ax.set_axisbelow(True)
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.00), ncol=2, frameon=False, fontsize=9)
    fig.savefig(out / 'score_components.png', dpi=180)
    plt.close(fig)

    cfg = read_json(ROOT / 'config.json')
    cutoff = dt(cfg['cutoff_utc'])
    start = dt('2026-01-01T00:00:00Z')
    end = dt('2026-01-03T13:00:00Z')
    hourly = [r for r in table('hourly_market.csv') if start <= dt(r['hour_utc']) <= end]
    fig, ax = plt.subplots(figsize=(11, 5.5), layout='constrained')
    ax.axvspan(cutoff, end, color='#e5e9ed', alpha=.7, label='Later trades (not used in the score)')
    ax.plot([dt(r['hour_utc']) for r in hourly], [float(r['yes_equivalent_vwap']) for r in hourly],
            color='#173a55', lw=2.4, label='Hourly average price on a YES scale')
    ax.axvline(cutoff, color='#bf692a', lw=1.6, ls='--', label='My cutoff: Jan 3, 05:30 UTC')
    evidence = table('top10_trade_evidence.csv')
    for r, color in zip(ranks[:3], ['#cb543d', '#227b8a', '#9d68ad']):
        last = max((t for t in evidence if t['wallet'] == r['wallet'] and t['side'] == 'BUY' and t['outcome'] == 'Yes'), key=lambda t: int(t['timestamp']))
        ax.scatter(dt(last['utc']), float(last['price']), s=48, color=color, zorder=4,
                   label=f"Wallet {r['rank']}: last YES buy before the cutoff")
    ax.set_xlim(start, end)
    ax.set_ylim(0, 1.04)
    ax.set_ylabel('Price on a YES scale (USDC per share)')
    ax.set_xlabel('UTC. Each point shows the start of the hour.')
    ax.set_title('Market prices before and after my cutoff', loc='left', pad=15)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12], tz=timezone.utc))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b\n%H:%M', tz=timezone.utc))
    ax.grid(axis='y', alpha=.15)
    ax.legend(loc='upper left', frameon=False, fontsize=9)
    fig.savefig(out / 'market_timeline.png', dpi=180)
    plt.close(fig)
    print('Saved figures/score_components.png and figures/market_timeline.png')


if __name__ == '__main__':
    main()
