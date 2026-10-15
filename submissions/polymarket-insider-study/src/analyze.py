import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from collect import ROOT, epoch, utc, read_json, write_csv


def load_trades(file):
    with file.open(encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['timestamp'] = int(r['timestamp'])
        for k in ('size', 'price', 'notional_usdc'):
            r[k] = float(r[k])
    return rows


def rank(rows, cutoff, cfg, hours=None, weights=None, target='Yes'):
    hours = hours or cfg['recent_hours']
    weights = weights or cfg['weights']
    groups = defaultdict(list)
    for r in rows:
        if r['timestamp'] < cutoff:
            groups[r['wallet']].append(r)
    ranked = []
    for wallet, trades in groups.items():
        recent = [r for r in trades if r['timestamp'] >= cutoff - hours * 3600]
        buys = [r for r in recent if r['side'] == 'BUY' and r['outcome'] == target]
        lifetime = [r for r in trades if r['side'] == 'BUY' and r['outcome'] == target]
        cash = sum(r['notional_usdc'] for r in buys)
        shares = sum(r['size'] for r in buys)
        all_cash = sum(r['notional_usdc'] for r in recent)
        lifetime_cash = sum(r['notional_usdc'] for r in lifetime)
        vwap = cash / shares if shares else 1.0
        features = {
            'size': min(1, math.log1p(cash / cfg['minimum_recent_yes_buy_usdc']) /
                        math.log1p(cfg['size_saturation_usdc'] / cfg['minimum_recent_yes_buy_usdc'])),
            'recency': cash / lifetime_cash if lifetime_cash else 0,
            'direction': cash / all_cash if all_cash else 0,
            'surprise': 1 - vwap,
        }
        eligible = cash >= cfg['minimum_recent_yes_buy_usdc']
        score = sum(weights[k] * features[k] for k in weights) if eligible else 0
        sells = [r for r in recent if r['side'] == 'SELL' and r['outcome'] == target]
        out = {'wallet': wallet, 'score': score, 'eligible': eligible,
               'recent_yes_buy_usdc': cash, 'recent_yes_buy_shares': shares,
               'recent_yes_buy_vwap': vwap if shares else '',
               'all_pre_cutoff_yes_buy_usdc': lifetime_cash,
               'recent_all_trade_notional_usdc': all_cash,
               'recent_yes_sell_shares': sum(r['size'] for r in sells),
               'recent_yes_sell_usdc': sum(r['notional_usdc'] for r in sells),
               'pre_cutoff_records': len(trades), 'recent_yes_buy_records': len(buys),
               'first_market_trade_utc': utc(min(r['timestamp'] for r in trades)),
               'last_recent_yes_buy_utc': utc(max(r['timestamp'] for r in buys)) if buys else '',
               'buy_and_hold_upside_scenario_usdc': shares - cash,
               'profile_url': 'https://polymarket.com/profile/' + wallet}
        out.update({k + '_feature': v for k, v in features.items()})
        out.update({k + '_points': weights[k] * features[k] if eligible else 0 for k in weights})
        ranked.append(out)
    ranked.sort(key=lambda r: (-r['score'], -r['recent_yes_buy_usdc'], r['wallet']))
    for i, r in enumerate(ranked, 1):
        r['rank'] = i
    return ranked


def main():
    cfg = read_json(ROOT / 'config.json')
    rows = load_trades(ROOT / 'artifacts/trades.csv')
    cutoff = epoch(cfg['cutoff_utc'])
    ranked = rank(rows, cutoff, cfg)
    write_csv(ROOT / 'artifacts/ranking.csv', ranked, ['rank'] + [k for k in ranked[0] if k != 'rank'])
    eligible = [r for r in ranked if r['eligible']]
    recent = [r for r in rows if cutoff - 86400 <= r['timestamp'] < cutoff]
    top = {r['wallet'] for r in ranked[:10]}
    evidence = [r for r in recent if r['wallet'] in top]
    write_csv(ROOT / 'artifacts/top10_trade_evidence.csv', evidence)
    sensitivity = []
    variants = [('cutoff_minus_60m', cutoff-3600, 24, None),
                ('cutoff_minus_30m', cutoff-1800, 24, None),
                ('base', cutoff, 24, None),
                ('cutoff_plus_30m', cutoff+1800, 24, None),
                ('window_12h', cutoff, 12, None), ('window_48h', cutoff, 48, None),
                ('equal_weights', cutoff, 24, dict.fromkeys(cfg['weights'], 25)),
                ('omit_size', cutoff, 24, {'size': 0, 'recency': 100/3, 'direction': 100/3, 'surprise': 100/3})]
    for name, cut, hours, weights in variants:
        rr = rank(rows, cut, cfg, hours, weights)
        index = {r['wallet']: r for r in rr}
        overlap = len(top & {r['wallet'] for r in rr[:10]})
        for base in ranked[:10]:
            r = index.get(base['wallet'])
            sensitivity.append({'scenario': name, 'cutoff_utc': utc(cut), 'recent_hours': hours,
                'wallet': base['wallet'], 'base_rank': base['rank'], 'scenario_rank': r['rank'] if r else '',
                'scenario_score': r['score'] if r else '', 'top10_overlap': overlap})
    write_csv(ROOT / 'artifacts/sensitivity.csv', sensitivity)
    placebo = []
    for day in range(0, 8):
        cut = cutoff - day * 86400
        rr = rank(rows, cut, cfg)
        ee = [r for r in rr if r['eligible']]
        placebo.append({'cutoff_utc': utc(cut), 'role': 'event' if day == 0 else 'earlier_day_comparison',
                        'eligible_wallets': len(ee), 'score_ge_80': sum(r['score'] >= 80 for r in ee),
                        'score_ge_90': sum(r['score'] >= 90 for r in ee),
                        'max_score': max((r['score'] for r in ee), default=0),
                        'top_wallet': rr[0]['wallet'] if rr else ''})
    write_csv(ROOT / 'artifacts/earlier_day_comparisons.csv', placebo)
    hourly = defaultdict(list)
    for r in rows:
        hourly[r['timestamp'] // 3600 * 3600].append(r)
    hourly_rows = []
    for t, trades in sorted(hourly.items()):
        shares = sum(r['size'] for r in trades)
        # Put NO trades on the YES price scale.
        yes_vwap = sum(r['size'] * (r['price'] if r['outcome'] == 'Yes' else 1-r['price']) for r in trades) / shares
        hourly_rows.append({'hour_utc': utc(t), 'records': len(trades), 'wallets': len(set(r['wallet'] for r in trades)),
                           'trade_notional_usdc': sum(r['notional_usdc'] for r in trades), 'yes_equivalent_vwap': yes_vwap})
    write_csv(ROOT / 'artifacts/hourly_market.csv', hourly_rows)
    history = []
    for r in ranked[:cfg['history_top_n']]:
        file = ROOT / f"artifacts/history/{r['wallet']}.csv"
        if not file.exists():
            continue
        h = load_trades(file)
        assert all(epoch(cfg['lookback_start_utc']) <= t['timestamp'] < cutoff for t in h)
        buys = [t for t in h if t['side'] == 'BUY']
        total = sum(t['notional_usdc'] for t in buys)
        focal = sum(t['notional_usdc'] for t in buys if t['condition_id'] == cfg['condition_id'])
        recent_h = [t for t in h if t['timestamp'] >= cutoff-86400 and t['side'] == 'BUY']
        recent_total = sum(t['notional_usdc'] for t in recent_h)
        focal_recent = sum(t['notional_usdc'] for t in recent_h if t['condition_id'] == cfg['condition_id'])
        history.append({'wallet': r['wallet'], 'rank': r['rank'], 'history_trade_rows': len(h),
            'distinct_markets': len(set(t['condition_id'] for t in h)),
            'first_observed_utc': utc(min(t['timestamp'] for t in h)) if h else '',
            'days_observed_to_cutoff': (cutoff-min(t['timestamp'] for t in h))/86400 if h else '',
            'all_market_buy_usdc': total, 'focal_market_buy_usdc': focal,
            'focal_buy_share': focal/total if total else '',
            'recent_all_market_buy_usdc': recent_total,
            'recent_focal_buy_share': focal_recent/recent_total if recent_total else ''})
    if history:
        write_csv(ROOT / 'artifacts/top10_history_context.csv', history)
    summary = {'market_records': len(rows), 'all_wallets': len(set(r['wallet'] for r in rows)),
               'pre_cutoff_records': sum(r['timestamp'] < cutoff for r in rows),
               'pre_cutoff_wallets_ranked': len(ranked), 'eligible_wallets': len(eligible),
               'recent_records': len(recent), 'score_ge_80': sum(r['score'] >= 80 for r in eligible),
               'score_ge_90': sum(r['score'] >= 90 for r in eligible),
               'observed_total_taker_notional_usdc': sum(r['notional_usdc'] for r in rows),
               'top10_recent_yes_buy_usdc': sum(r['recent_yes_buy_usdc'] for r in ranked[:10])}
    (ROOT / 'artifacts/analysis_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    for r in ranked[:10]:
        print(r['rank'], r['wallet'], round(r['score'], 2), round(r['recent_yes_buy_usdc'], 2), r['last_recent_yes_buy_utc'])


if __name__ == '__main__':
    main()
