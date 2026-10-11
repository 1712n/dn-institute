"""Draw the report's process, timeline and score contributions from saved results.

Run after src/run.py. No network access or analytical recalculation is performed.
"""

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
CONFIG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8-sig'))
LOG = json.loads((ROOT / 'data/prepared/run_log.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'figure.facecolor': '#ffffff', 'axes.facecolor': '#ffffff',
                     'text.color': '#172b40', 'axes.labelcolor': '#172b40'})


def save(fig, name):
    fig.savefig(OUT / name, dpi=160, bbox_inches='tight', facecolor='white')
    from matplotlib.text import Text
    for item in fig.findobj(match=Text):
        item.set_text(english_label(item.get_text()))
    # Tick formatters can restore their original labels when the figure is drawn.
    for ax in fig.axes:
        labels = [item.get_text() for item in ax.get_yticklabels()]
        if any(re.search('[А-Яа-яЁё]', label) for label in labels):
            ax.set_yticks(ax.get_yticks(), [english_label(label) for label in labels])
    english_name = Path(name).stem + '_en.png'
    fig.savefig(OUT / english_name, dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def english_label(label):
    translations = {
        'Как сделки превращаются в два рейтинга': 'From trades to two rankings',
        'на основном рынке': 'on the main market',
        'порог 100 USDC': '100 USDC threshold',
        'Предыдущие сделки': 'Trading history',
        '↓ шесть эвристик': '↓ six heuristics',
        'обычные веса': 'original weights',
        'веса пересчитаны': 'rescaled weights',
        'Отбор определяет, кого изучаем. Эвристики определяют порядок ручной проверки.':
            'Selection identifies candidates. Heuristics set priorities for manual review.',
        'С чем сравниваем последние сделки': 'Comparison period for recent trades',
        'Сделки в 05:00 3 января и позже в основной балл не входят.':
            'Trades at or after 05:00 UTC on January 3 are excluded from the main score.',
        'Время': 'Timing', 'Размер': 'Size', 'Направленность': 'Direction',
        'Объем': 'Own volume', 'Активность': 'Activity', 'Концентрация': 'Concentration',
        'Из чего складывается балл первых трех кандидатов': 'Score contributions for the top three candidates',
        'Все шесть эвристик': 'All six heuristics',
        'Только доступные эвристики — веса пересчитаны': 'Available heuristics only — rescaled weights',
        'Баллы (максимум 100)': 'Score (maximum 100)',
        'Две самостоятельные группы: более высокий балл внизу не означает более сильное основание.':
            'Two separate groups: a higher score below does not imply stronger evidence.',
    }
    for source, target in sorted(translations.items(), key=lambda pair: len(pair[0]), reverse=True):
        label = label.replace(source, target)
    patterns = [
        (r'([\d ]+) кошельков', r'\1 wallets'),
        (r'(\d+) кандидатов', r'\1 candidates'),
        (r'Все эвристики: (\d+)', r'All heuristics: \1'),
        (r'Есть пропуски: (\d+)', r'Missing values: \1'),
        (r'Предыдущая торговля: ([\d.]+) суток', r'Previous trading: \1 days'),
        (r'Отбор: ([\d.]+) суток', r'Selection: \1 days'),
        (r'Кандидат (\d+)', r'Candidate \1'),
    ]
    for pattern, replacement in patterns:
        label = re.sub(pattern, replacement, label)
    return label


def process():
    counts = LOG['ranking_summary']
    n = LOG['screening_summary']['observed_wallets_before_cutoff']
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set(xlim=(0, 11), ylim=(0, 4.5))
    ax.axis('off')
    ax.text(0, 4.2, 'Как сделки превращаются в два рейтинга', fontsize=18, weight='bold')
    def box(x, y, w, label, color='#edf3fa'):
        ax.add_patch(FancyBboxPatch((x, y), w, 1.15, boxstyle='round,pad=0.06',
                                   facecolor=color, edgecolor='#ccdae8'))
        ax.text(x+w/2, y+.575, label, ha='center', va='center', fontsize=11)
    def arrow(x1,y1,x2,y2):
        ax.annotate('', (x2,y2), (x1,y1), arrowprops={'arrowstyle':'->', 'color':'#627990', 'lw':1.6})
    box(.1, 1.8, 2.1, f'{n:,} кошельков'.replace(',', ' ')+'\nна основном рынке\nprepare.py')
    box(2.65, 1.8, 2.0, f"{counts['ranked_wallets']} кандидатов\nпорог 100 USDC\nprepare.py")
    box(5.1, 1.8, 2.45, 'Предыдущие сделки\ncollect.py\n↓ шесть эвристик\nmetrics.py')
    box(8.1, 2.5, 2.7, f"Все эвристики: {counts['complete_coverage_wallets']}\nобычные веса\nranking.py", '#e8f3ee')
    box(8.1, .8, 2.7, f"Есть пропуски: {counts['incomplete_coverage_wallets']}\nвеса пересчитаны\nranking.py", '#fff2df')
    arrow(2.22,2.375,2.56,2.375)
    arrow(4.72,2.375,5.02,2.375)
    arrow(7.62,2.375,8.01,3.075)
    arrow(7.62,2.375,8.01,1.375)
    ax.text(.1,.15,'Отбор определяет, кого изучаем. Эвристики определяют порядок ручной проверки.', fontsize=11)
    save(fig, 'process.png')


def timeline():
    start = pd.Timestamp(CONFIG['candidate_history']['effective_baseline_start_inclusive_utc'])
    cutoff = pd.Timestamp(CONFIG['analysis_cutoff'])
    recent = cutoff-pd.Timedelta(hours=CONFIG['data_preparation']['screening_window_hours'])
    base_days=(recent-start).total_seconds()/86400
    recent_days=(cutoff-recent).total_seconds()/86400
    fig, ax=plt.subplots(figsize=(11,2.9))
    ax.set(xlim=(-.4,base_days+recent_days+.4),ylim=(-.9,1.7))
    ax.axis('off')
    ax.text(0,1.35,'С чем сравниваем последние сделки',fontsize=18,weight='bold')
    ax.barh(.5,base_days,left=0,height=.48,color='#dce9f7')
    ax.barh(.5,recent_days,left=base_days,height=.48,color='#f3c984')
    ax.text(base_days/2,.5,f'Предыдущая торговля: {base_days:g} суток',ha='center',va='center')
    ax.text(base_days+recent_days/2,.5,f'Отбор: {recent_days:g} суток',ha='center',va='center')
    for x,date in [(0,start),(base_days,recent),(base_days+recent_days,cutoff)]:
        ax.plot([x,x],[.13,.83],color='#627990',lw=1)
        ax.text(x,-.03,date.strftime('%d.%m.%Y\n%H:%M UTC'),ha='center',va='top',fontsize=10)
    ax.text(0,-.77,'Сделки в 05:00 3 января и позже в основной балл не входят.',fontsize=11)
    save(fig,'timeline.png')


def contributions():
    labels=['Время','Размер','Направленность','Объем','Активность','Концентрация']
    colors=['#4178ad','#8eb7d8','#f2ba59','#2f997f','#86bba7','#aa87b8']
    metrics=['metric_timing','metric_size','metric_direction','metric_volume','metric_activity','metric_concentration']
    assert set(metrics) == set(CONFIG['ranking']['weights'])
    fig,axes=plt.subplots(2,1,figsize=(11,7))
    fig.suptitle('Из чего складывается балл первых трех кандидатов',fontsize=17,weight='bold',y=.99)
    for ax,group,title in zip(axes,['complete','incomplete'],['Все шесть эвристик','Только доступные эвристики — веса пересчитаны']):
        rows=pd.read_csv(ROOT/'results'/f'ranking_{group}.csv').head(3)
        positions=np.arange(len(rows))
        left=np.zeros(len(rows))
        for metric,label,color in zip(metrics,labels,colors):
            values=rows[metric.replace('metric_','contribution_')].to_numpy()
            ax.barh(positions,values,left=left,color=color,label=label,height=.55)
            left+=values
        np.testing.assert_allclose(left,rows['score'],atol=1e-10)
        ax.set_yticks(positions,[f'Кандидат {int(row.rank)}' for row in rows.itertuples()])
        ax.invert_yaxis()
        ax.set_xlim(0,110)
        ax.set_xticks([0,20,40,60,80,100])
        ax.set_xlabel('Баллы (максимум 100)')
        ax.set_title(title,loc='left',fontsize=12,weight='bold',pad=12)
        ax.spines[['top','right','left']].set_visible(False)
        ax.grid(axis='x',alpha=.15)
        ax.set_axisbelow(True)
        for pos,score in zip(positions,left):
            ax.text(score+1,pos,f'{score:.2f}',va='center',fontsize=10)
    handles,legend=axes[0].get_legend_handles_labels()
    fig.legend(handles,legend,ncol=3,loc='lower center',bbox_to_anchor=(.5,.015),frameon=False)
    fig.text(.5,.005,'Две самостоятельные группы: более высокий балл внизу не означает более сильное основание.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.13,1,.95),h_pad=2)
    save(fig,'score_contributions.png')


if __name__ == '__main__':
    process()
    timeline()
    contributions()
    print(f'Created three figures in Russian and English in {OUT}')
