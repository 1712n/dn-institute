"""Reproducible retrospective triage; standard-library Python 3.10+.

Scores are investigation priorities, NOT probabilities or accusations.
Run from this directory: python3 analyze.py
"""
import collections
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
PRIMARY = '0x580adc1327de9bf7c179ef5aaffa3377bb5cb252b7d6390b027172d43fd6f993'
DAY = 86400

CSV_FIELDS = {'duplicate_collapse_sensitivity.csv': ['wallet',
                                        'eligible',
                                        'score',
                                        'buy_yes_notional',
                                        'buy_yes_shares',
                                        'yes_buy_vwap',
                                        'baseline_7d_buy_yes_notional',
                                        'net_directional_share_flow',
                                        'net_yes_share_flow',
                                        'size_factor',
                                        'cheapness',
                                        'burst',
                                        'directionality',
                                        'window_trade_rows',
                                        'window_yes_buy_rows',
                                        'first_observed_in_this_market_utc',
                                        'eligibility_reason',
                                        'history_scope',
                                        'rank'],
 'event_timeline.csv': ['event', 'timestamp_utc', 'interpretation', 'source'],
 'hourly_activity.csv': ['hour_utc', 'rows', 'wallets', 'yes_buy_notional', 'yes_trade_vwap'],
 'market_coverage.csv': ['dataset',
                         'condition_id',
                         'question',
                         'created_at',
                         'pages',
                         'rows',
                         'wallets',
                         'first_trade_utc',
                         'last_trade_utc',
                         'hashes_match',
                         'cursor_exhausted',
                         'csv_reconciled'],
 'news_boundary_sensitivity.csv': ['cutoff_utc',
                                   'window_hours',
                                   'interpretation',
                                   'eligible',
                                   'max_score',
                                   'base_top3_overlap',
                                   'leading_wallet'],
 'placebo_windows.csv': ['cutoff_utc',
                         'days_before_event',
                         'eligible',
                         'max_score',
                         'score_ge_70',
                         'score_ge_80'],
 'primary_trades.csv': ['evidence_id',
                        'proxy_wallet',
                        'condition_id',
                        'token_id',
                        'side',
                        'size',
                        'price',
                        'timestamp',
                        'outcome',
                        'transaction_hash'],
 'sensitivity_ranks.csv': ['scenario', 'wallet', 'rank', 'score'],
 'sensitivity_summary.csv': ['scenario',
                             'cutoff_utc',
                             'eligible',
                             'top10_overlap',
                             'max_score',
                             'score_ge_70'],
 'top_wallet_related_markets.csv': ['wallet', 'question', 'rows_before_cutoff', 'buy_yes_notional'],
 'top_wallet_window_trades.csv': ['evidence_id',
                                  'proxy_wallet',
                                  'condition_id',
                                  'token_id',
                                  'side',
                                  'size',
                                  'price',
                                  'timestamp',
                                  'outcome',
                                  'transaction_hash'],
 'wallet_ranking.csv': ['wallet',
                        'eligible',
                        'score',
                        'buy_yes_notional',
                        'buy_yes_shares',
                        'yes_buy_vwap',
                        'baseline_7d_buy_yes_notional',
                        'net_directional_share_flow',
                        'net_yes_share_flow',
                        'size_factor',
                        'cheapness',
                        'burst',
                        'directionality',
                        'window_trade_rows',
                        'window_yes_buy_rows',
                        'first_observed_in_this_market_utc',
                        'eligibility_reason',
                        'history_scope',
                        'rank']}


def ts(s):
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()


CUTOFF = ts('2026-01-03T05:00:00Z')
START = ts('2025-11-01T00:00:00Z')
END = ts('2026-05-02T00:00:00Z')


def write_csv(name, rows, fields=None):
    rows = list(rows)
    fields = fields or CSV_FIELDS.get(name)
    if fields is None:
        if not rows:
            raise ValueError('CSV fields required for empty output: ' + name)
        fields = list(rows[0])
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)


def load_verified(label):
    root = ROOT / 'data' / label
    manifest = json.loads((root / 'manifest.json').read_text())
    if manifest['status'] != 'collected':
        raise ValueError('Incomplete input: ' + label)
    raw_rows, coverage, expected_cursors = [], [], {}
    for source in manifest['sources']:
        raw = (root / source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source['sha256']:
            raise ValueError('Hash mismatch: ' + source['path'])
        payload = json.loads(raw)
        if 'market_' not in source['path']:
            continue
        query = parse_qs(urlparse(source['url']).query)
        condition = query['condition'][0]
        if query.get('cursor', [None])[0] != expected_cursors.get(condition):
            raise ValueError('Broken cursor chain')
        expected_cursors[condition] = payload['pagination']['next_cursor']
        if expected_cursors[condition] is None and payload['pagination'].get('has_more'):
            raise ValueError('Inconsistent terminal page')
        for index, row in enumerate(payload['data']):
            if row['condition_id'] != condition:
                raise ValueError('Wrong-market row')
            if START <= int(row['timestamp']) < END:
                row = dict(row)
                row['evidence_id'] = f"{label}/{source['path']}#{index}"
                raw_rows.append(row)
    if any(v is not None for v in expected_cursors.values()):
        raise ValueError('Unfinished pagination')
    with (root / 'trades.csv').open() as f:
        reader = csv.DictReader(f); csv_rows = list(reader); fields = reader.fieldnames
    normalize = lambda r: tuple(str(r.get(k, '')) for k in fields)
    if collections.Counter(map(normalize, raw_rows)) != collections.Counter(map(normalize, csv_rows)):
        raise ValueError('CSV does not reconcile to raw records')
    if len(raw_rows) != manifest['rows_in_window']:
        raise ValueError('Manifest row-count mismatch')
    for m in manifest['markets']:
        rows = [r for r in raw_rows if r['condition_id'] == m['condition_id']]
        coverage.append(dict(dataset=label, condition_id=m['condition_id'], question=m['question'],
            created_at=m['created_at'], pages=m['pages'], rows=len(rows),
            wallets=len({r['proxy_wallet'] for r in rows}),
            first_trade_utc=iso(min(r['timestamp'] for r in rows)) if rows else '',
            last_trade_utc=iso(max(r['timestamp'] for r in rows)) if rows else '',
            hashes_match=True, cursor_exhausted=True, csv_reconciled=True))
    return raw_rows, coverage


def rank(rows, cutoff=CUTOFF, weights=(.4, .3, .3), min_buy=500, window_hours=24):
    """All market wallets included; eligible ranks use only pre-cutoff trades.

Cash is gross observed BUY YES notional. Direction is signed share flow.
Missing transfers/positions mean share flow is NOT an inventory balance.
"""
    if window_hours <= 0:
        raise ValueError('Window must be positive')
    window_seconds = window_hours * 3600
    wallets = collections.defaultdict(list)
    for r in rows:
        wallets[r['proxy_wallet']].append(r)
    result = []
    for wallet, history in wallets.items():
        window = [r for r in history if cutoff-window_seconds <= r['timestamp'] < cutoff]
        baseline = [r for r in history if cutoff-window_seconds-7*DAY <= r['timestamp'] < cutoff-window_seconds]
        buys = [r for r in window if r['side']=='BUY' and r['outcome']=='Yes']
        cash = sum(r['price']*r['size'] for r in buys)
        shares = sum(r['size'] for r in buys)
        prior = sum(r['price']*r['size'] for r in baseline if r['side']=='BUY' and r['outcome']=='Yes')
        positive = sum(r['size'] for r in window if (r['side']=='BUY') == (r['outcome']=='Yes'))
        negative = sum(r['size'] for r in window if (r['side']=='BUY') != (r['outcome']=='Yes'))
        net = positive-negative
        yes_sells = sum(r['size'] for r in window if r['side']=='SELL' and r['outcome']=='Yes')
        net_yes = shares-yes_sells
        vwap = cash/shares if shares else None
        size_factor = min(1., math.log1p(cash)/math.log1p(10000.))
        cheap = 1-vwap if vwap is not None else 0.
        burst = cash/(cash+prior/7+1000.)
        direction = max(0., net/(positive+negative)) if positive+negative else 0.
        eligible = cash >= min_buy and net > 0 and net_yes > 0
        score = 100*size_factor*sum(w*x for w,x in zip(weights,(cheap,burst,direction))) if eligible else 0.
        observed = [r['timestamp'] for r in history if r['timestamp'] < cutoff]
        result.append(dict(wallet=wallet,eligible=eligible,score=round(score,6),
            buy_yes_notional=round(cash,6),buy_yes_shares=round(shares,6),
            yes_buy_vwap=round(vwap,8) if vwap is not None else '',
            baseline_7d_buy_yes_notional=round(prior,6),
            net_directional_share_flow=round(net,6),net_yes_share_flow=round(net_yes,6),
            size_factor=round(size_factor,8),cheapness=round(cheap,8),
            burst=round(burst,8),directionality=round(direction,8),
            window_trade_rows=len(window),window_yes_buy_rows=len(buys),
            first_observed_in_this_market_utc=iso(min(observed)) if observed else '',
            eligibility_reason='eligible' if eligible else ('no_window_yes_buy' if not buys else
                ('below_notional_threshold' if cash < min_buy else 'nonpositive_net_flow')),
            history_scope='this_market_only; wallet_age_unknown'))
    result.sort(key=lambda r:(-r['score'],r['wallet']))
    last_score, dense_rank = None, 0
    for r in result:
        if r['eligible']:
            if r['score'] != last_score: dense_rank += 1
            last_score = r['score']; r['rank'] = dense_rank
        else: r['rank'] = ''
    return result


def main():
    OUT.mkdir(exist_ok=True)
    all_rows, coverage = [], []
    for label in ['maduro','custody']:
        r,c = load_verified(label); all_rows.extend(r); coverage.extend(c)
    write_csv('market_coverage.csv', coverage)
    primary = [r for r in all_rows if r['condition_id']==PRIMARY]
    keys = ['proxy_wallet','condition_id','token_id','side','size','price','timestamp','transaction_hash']
    signatures=collections.Counter(tuple(str(r[k]) for k in keys) for r in primary)
    duplicate_excess=sum(n-1 for n in signatures.values())
    for r in primary:
        if r['outcome'] not in ('Yes','No') or r['side'] not in ('BUY','SELL'):
            raise ValueError('Invalid categorical value')
        if not (math.isfinite(r['size']) and r['size']>0 and math.isfinite(r['price']) and 0<=r['price']<=1):
            raise ValueError('Invalid price/size')
    ranked = rank(primary)
    write_csv('wallet_ranking.csv', ranked)
    evidence_fields = ['evidence_id','proxy_wallet','condition_id','token_id','side','size','price','timestamp','outcome','transaction_hash']
    write_csv('primary_trades.csv', primary, evidence_fields)
    top = {r['wallet'] for r in ranked if r['eligible'] and r['rank']<=10}
    flagged = [r for r in primary if r['proxy_wallet'] in top and CUTOFF-DAY <= r['timestamp'] < CUTOFF]
    write_csv('top_wallet_window_trades.csv', flagged, evidence_fields)
    cases = [('earlier_0400',CUTOFF-3600,(.4,.3,.3),500),
             ('base_0500',CUTOFF,(.4,.3,.3),500),
             ('strike_boundary_0600',CUTOFF+3600,(.4,.3,.3),500),
             ('announcement_0921_contaminated',ts('2026-01-03T09:21:00Z'),(.4,.3,.3),500),
             ('equal_weights',CUTOFF,(1/3,1/3,1/3),500),
             ('burst_heavy',CUTOFF,(.2,.5,.3),500),
             ('minimum_100',CUTOFF,(.4,.3,.3),100),
             ('minimum_1000',CUTOFF,(.4,.3,.3),1000)]
    sensitivity=[]; comparison=[]
    for name,cutoff,weights,minimum in cases:
        rr=rank(primary,cutoff,weights,minimum)
        selected=[r for r in rr if r['eligible']]
        best={r['wallet'] for r in selected[:10]}
        comparison.append(dict(scenario=name,cutoff_utc=iso(cutoff),eligible=len(selected),
            top10_overlap=len(best & top),max_score=selected[0]['score'] if selected else 0,
            score_ge_70=sum(r['score']>=70 for r in selected)))
        for r in selected:
            sensitivity.append(dict(scenario=name,wallet=r['wallet'],rank=r['rank'],score=r['score']))
    write_csv('sensitivity_summary.csv',comparison)
    write_csv('sensitivity_ranks.csv',sensitivity)
    # Earlier cutoffs test sensitivity to uncertain information arrival. Later
    # cutoffs are explicitly contaminated comparison windows, never evidence
    # that all trades preceded public information.
    boundary=[]
    base_top3={r['wallet'] for r in ranked if r['eligible'] and r['rank']<=3}
    for hour,minute in [(0,0),(3,0),(4,0),(5,0),(5,30),(6,0),(7,30)]:
        cutoff=ts(f'2026-01-03T{hour:02d}:{minute:02d}:00Z')
        selected=[r for r in rank(primary,cutoff) if r['eligible']]
        boundary.append(dict(cutoff_utc=iso(cutoff),window_hours=24,
            interpretation='conservative sensitivity' if cutoff<CUTOFF else
                ('main analysis' if cutoff==CUTOFF else 'closer to or after visible events; not a clean-news boundary'),
            eligible=len(selected),max_score=selected[0]['score'] if selected else 0,
            base_top3_overlap=len(base_top3 & {r['wallet'] for r in selected[:3]}),
            leading_wallet=selected[0]['wallet'] if selected else ''))
    for hours in [12,48]:
        selected=[r for r in rank(primary,window_hours=hours) if r['eligible']]
        boundary.append(dict(cutoff_utc=iso(CUTOFF),window_hours=hours,
            interpretation='window-length sensitivity',eligible=len(selected),
            max_score=selected[0]['score'] if selected else 0,
            base_top3_overlap=len(base_top3 & {r['wallet'] for r in selected[:3]}),
            leading_wallet=selected[0]['wallet'] if selected else ''))
    write_csv('news_boundary_sensitivity.csv',boundary)
    placebo=[]
    for days in range(8):
        rr=[r for r in rank(primary,CUTOFF-days*DAY) if r['eligible']]
        placebo.append(dict(cutoff_utc=iso(CUTOFF-days*DAY),days_before_event=days,
            eligible=len(rr),max_score=rr[0]['score'] if rr else 0,
            score_ge_70=sum(r['score']>=70 for r in rr),
            score_ge_80=sum(r['score']>=80 for r in rr)))
    write_csv('placebo_windows.csv',placebo)
    hourly=collections.defaultdict(list)
    for r in primary:
        if CUTOFF-2*DAY<=r['timestamp']<CUTOFF+DAY:
            hourly[r['timestamp']//3600*3600].append(r)
    write_csv('hourly_activity.csv',[
        dict(hour_utc=iso(t),rows=len(rr),wallets=len({r['proxy_wallet'] for r in rr}),
            yes_buy_notional=sum(r['price']*r['size'] for r in rr if r['side']=='BUY' and r['outcome']=='Yes'),
            yes_trade_vwap=sum(r['price']*r['size'] for r in rr if r['outcome']=='Yes')/
                sum(r['size'] for r in rr if r['outcome']=='Yes') if any(r['outcome']=='Yes' for r in rr) else '')
        for t,rr in sorted(hourly.items())])
    # Same-signature collapse is a sensitivity analysis only: API lacks log index.
    unique={tuple(str(r[k]) for k in keys):r for r in primary}
    collapsed=rank(list(unique.values()))
    write_csv('duplicate_collapse_sensitivity.csv',collapsed)
    cross=[]
    for wallet in sorted(top):
        for c in coverage:
            rr=[r for r in all_rows if r['proxy_wallet']==wallet and r['condition_id']==c['condition_id'] and r['timestamp']<CUTOFF]
            cross.append(dict(wallet=wallet,question=c['question'],rows_before_cutoff=len(rr),
                buy_yes_notional=sum(r['price']*r['size'] for r in rr if r['side']=='BUY' and r['outcome']=='Yes')))
    write_csv('top_wallet_related_markets.csv',cross)
    summary=dict(total_rows=len(all_rows),primary_rows=len(primary),primary_wallets=len(ranked),
        all_wallets=len({r['proxy_wallet'] for r in all_rows}),
        eligible=sum(r['eligible'] for r in ranked),duplicate_signature_excess=duplicate_excess,
        top10_collapsed_overlap=len(top & {r['wallet'] for r in collapsed if r['eligible'] and r['rank']<=10}),
        primary_pre_cutoff_rows=sum(r['timestamp']<CUTOFF for r in primary),
        top10=ranked[:10],sensitivity=comparison,placebos=placebo)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
