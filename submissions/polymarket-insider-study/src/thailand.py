"""Rebuild the Thailand tables from saved data. --collect refreshes missing API data."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
import analyze
from analyze import load_trades, rank
from collect import Client, collect_windows, epoch, normalize, read_json, utc, write_csv

ROOT = Path(__file__).resolve().parents[1] / 'cases/thailand'
FOCUS = '0x1cfc6f041b5b8dad3c14b867be8482a69d45b8e0'


def collect(cfg):
    client = Client(ROOT)
    events = client.get('https://gamma-api.polymarket.com/events',
                        {'slug': cfg['event_slug'], 'closed': 'true'})
    market = next(m for e in events for m in e['markets'] if m['id'] == cfg['market_id'])
    if market['conditionId'] != cfg['condition_id']:
        raise ValueError('Market condition ID does not match config')
    (ROOT / 'data/market.json').write_text(json.dumps(market, indent=2), encoding='utf-8')
    coverage = []
    rows = collect_windows(lambda p: client.get('https://data-api.polymarket.com/trades', p),
        {'market': cfg['condition_id'], 'takerOnly': 'true'}, epoch(cfg['start_utc']),
        epoch(cfg['end_exclusive_utc']) - 1, 1000, coverage, cfg['market_id'])
    write_csv(ROOT / 'artifacts/trades.csv', normalize(rows))
    write_csv(ROOT / 'artifacts/coverage.csv', coverage)
    coverage = []
    for wallet in cfg['full_history_wallets']:
        rows = collect_windows(lambda p: client.get('https://data-api.polymarket.com/activity', p),
            {'user': wallet, 'type': 'TRADE', 'sortBy': 'TIMESTAMP', 'sortDirection': 'ASC'},
            epoch(cfg['lookback_start_utc']), epoch(cfg['cutoff_utc']) - 1, 500, coverage, wallet)
        write_csv(ROOT / f'artifacts/history/{wallet}.csv', normalize(rows))
    write_csv(ROOT / 'artifacts/history_coverage.csv', coverage)
    for label, direction, start in [('earliest', 'ASC', epoch(cfg['lookback_start_utc'])),
                                     ('recent', 'DESC', epoch(cfg['cutoff_utc']) - 86400)]:
        params = {'user': cfg['sample_history_wallet'], 'type': 'TRADE',
                  'sortBy': 'TIMESTAMP', 'sortDirection': direction, 'start': start,
                  'end': epoch(cfg['cutoff_utc']) - 1, 'limit': 100, 'offset': 0}
        rows = client.get('https://data-api.polymarket.com/activity', params)
        if any(not start <= r['timestamp'] <= params['end'] or
               r['proxyWallet'].lower() != params['user'] for r in rows):
            raise ValueError('History sample failed bounds validation')
        suffix = '-earliest' if label == 'earliest' else ''
        write_csv(ROOT / f"artifacts/history_sample/{params['user']}{suffix}.csv", normalize(rows))


def check_transaction(rows):
    saved = read_json(ROOT / 'data/transaction_check.json')
    receipt, block = saved['receipt']['result'], saved['block']['result']
    if receipt['status'] != '0x1' or receipt['blockHash'] != block['hash']:
        raise ValueError('Transaction failed or block mismatch')
    matched = [r for r in rows if r['transaction_hash'] == receipt['transactionHash']
               and r['wallet'] == FOCUS]
    if len(matched) != 1:
        raise ValueError('Expected one matching API row')
    row = matched[0]
    cash_out, shares_in = 0, 0
    for log in receipt['logs']:
        topics = [t.lower() for t in log['topics']]
        if not topics:
            continue
        # ERC-20 Transfer(address,address,uint256), historical bridged USDC.
        if (log['address'].lower() == '0x2791bca1f2de4661ed88a30c99a7a9449aa84174'
                and topics[0] == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'):
            amount = int(log['data'], 16)
            if topics[1][-40:] == FOCUS[2:]: cash_out += amount
            if topics[2][-40:] == FOCUS[2:]: cash_out -= amount
        # ERC-1155 TransferSingle(operator,from,to,id,value).
        if (log['address'].lower() == '0x4d97dcd97ec945f40cf65f87097ace5ea0476045'
                and topics[0] == '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62'):
            data = log['data'][2:]
            token, amount = int(data[:64], 16), int(data[64:128], 16)
            if token == int(row['asset']):
                if topics[3][-40:] == FOCUS[2:]: shares_in += amount
                if topics[2][-40:] == FOCUS[2:]: shares_in -= amount
    cash_out, shares_in = cash_out / 1e6, shares_in / 1e6
    if (abs(cash_out - row['notional_usdc']) > 0.00001 or
            abs(shares_in - row['size']) > 0.000001 or
            int(block['timestamp'], 16) != row['timestamp']):
        raise ValueError('Blockchain transfers do not match API row')
    return {'transaction_hash': row['transaction_hash'], 'utc': row['utc'],
            'wallet': FOCUS, 'net_usdc_out': cash_out, 'net_yes_shares_in': shares_in,
            'receipt_status': receipt['status'], 'api_match': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect', action='store_true')
    args = parser.parse_args()
    cfg = read_json(ROOT / 'config.json')
    if args.collect:
        collect(cfg)
    analyze.ROOT = ROOT
    analyze.main()
    rows = load_trades(ROOT / 'artifacts/trades.csv')
    cutoff = epoch(cfg['cutoff_utc'])
    h = load_trades(ROOT / f'artifacts/history/{FOCUS}.csv')
    if any(not epoch(cfg['lookback_start_utc']) <= r['timestamp'] < cutoff or
           r['wallet'] != FOCUS for r in h):
        raise ValueError('Focus history failed bounds validation')
    daily = defaultdict(list)
    for r in h:
        daily[(r['utc'][:10], r['market_slug'], r['side'], r['outcome'])].append(r)
    daily_rows = [{'date_utc': key[0], 'market_slug': key[1], 'side': key[2],
                  'outcome': key[3], 'records': len(rr),
                  'shares': sum(r['size'] for r in rr),
                  'notional_usdc': sum(r['notional_usdc'] for r in rr)}
                 for key, rr in sorted(daily.items())]
    write_csv(ROOT / 'artifacts/focus_daily_trades.csv', daily_rows)
    bjt = [r for r in h if r['condition_id'] == cfg['condition_id'] and r['side'] == 'BUY']
    cash = sum(r['notional_usdc'] for r in bjt)
    recent = [r for r in bjt if r['timestamp'] >= cutoff - 72 * 3600]
    summary = {'wallet': FOCUS, 'history_rows': len(h), 'history_markets': len(set(r['condition_id'] for r in h)),
               'first_observed_utc': min(r['utc'] for r in h),
               'history_sell_records': sum(r['side'] == 'SELL' for r in h),
               'bjt_buy_records': len(bjt), 'bjt_buy_usdc': cash,
               'bjt_buy_shares': sum(r['size'] for r in bjt),
               'bjt_buy_vwap': cash / sum(r['size'] for r in bjt),
               'bjt_last_72h_buy_usdc': sum(r['notional_usdc'] for r in recent),
               'bjt_last_72h_buy_share': sum(r['notional_usdc'] for r in recent) / cash,
               'other_buy_usdc': sum(r['notional_usdc'] for r in h if r['side'] == 'BUY' and r['condition_id'] != cfg['condition_id'])}
    (ROOT / 'artifacts/focus_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    tx = check_transaction(rows)
    (ROOT / 'artifacts/transaction_check.json').write_text(json.dumps(tx, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print(json.dumps(tx, indent=2))


if __name__ == '__main__':
    main()
