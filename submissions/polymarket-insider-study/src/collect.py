"""Public, unauthenticated read-only collector. Python 3.10+, standard library only."""
import argparse
import csv
import gzip
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def epoch(value):
    return int(datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp())


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace('+00:00', 'Z')


def write_csv(path, rows, fields=None):
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


class Client:
    def __init__(self, root=ROOT):
        self.root = root
        self.cache = root / 'data/raw'
        self.cache.mkdir(parents=True, exist_ok=True)
        self.manifest = root / 'data/request_manifest.jsonl'

    def get(self, base, params):
        url = base + '?' + urllib.parse.urlencode(sorted(params.items()))
        key = hashlib.sha256(url.encode()).hexdigest()
        file = self.cache / (key + '.json.gz')
        if file.exists():
            with gzip.open(file, 'rt', encoding='utf-8') as f:
                return json.load(f)
        for attempt in range(5):
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (public research; read-only)',
                    'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=45) as response:
                    body = response.read()
                data = json.loads(body)
                break
            except (urllib.error.URLError, TimeoutError) as exc:
                if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                    raise
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        with gzip.open(file, 'wb') as f:
            f.write(body)
        entry = {'url': url, 'retrieved_utc': utc(int(time.time())),
                 'response_sha256': hashlib.sha256(body).hexdigest(),
                 'raw_file': file.relative_to(self.root).as_posix(),
                 'records': len(data) if isinstance(data, list) else None}
        with self.manifest.open('a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        time.sleep(0.12)
        return data


def collect_windows(fetch, base_params, start, end, limit, coverage, label):
    """Inclusive, disjoint windows. Never silently accept a capped response.

    Exact repeated rows within an API response are retained: no log index is
    supplied, so equal-valued fills cannot safely be collapsed. Saturated
    one-second windows fail closed instead of silently truncating.
    """
    data = fetch({**base_params, 'start': start, 'end': end, 'limit': limit, 'offset': 0})
    if not isinstance(data, list):
        raise ValueError(f'Expected list for {label}: {str(data)[:200]}')
    for row in data:
        if not start <= int(row['timestamp']) <= end:
            raise ValueError(f'API ignored timestamp bounds for {label}')
        if base_params.get('market') and row['conditionId'].lower() != base_params['market'].lower():
            raise ValueError('Unexpected market')
        if base_params.get('user') and row['proxyWallet'].lower() != base_params['user'].lower():
            raise ValueError('Unexpected wallet')
    if len(data) >= limit:
        if start == end:
            raise ValueError('Saturated one-second window: require a log-index/cursor source')
        middle = (start + end) // 2
        return (collect_windows(fetch, base_params, start, middle, limit, coverage, label)
                + collect_windows(fetch, base_params, middle + 1, end, limit, coverage, label))
    coverage.append({'scope': label, 'start_utc': utc(start), 'end_inclusive_utc': utc(end),
                     'records': len(data), 'limit': limit, 'exhausted_below_cap': True})
    return data


def normalize(rows):
    result = []
    for i, r in enumerate(rows):
        q, p = float(r['size']), float(r['price'])
        if q < 0 or not 0 <= p <= 1 or r['side'] not in ('BUY', 'SELL'):
            raise ValueError('Invalid trade values')
        result.append({
            'record_id': i + 1, 'timestamp': int(r['timestamp']), 'utc': utc(int(r['timestamp'])),
            'wallet': r['proxyWallet'].lower(), 'condition_id': r['conditionId'].lower(),
            'asset': r['asset'], 'side': r['side'], 'outcome': r['outcome'],
            'outcome_index': r['outcomeIndex'], 'size': r['size'], 'price': r['price'],
            'notional_usdc': q * p, 'transaction_hash': r['transactionHash'].lower(),
            'transaction_url': 'https://polygonscan.com/tx/' + r['transactionHash'].lower(),
            'market_slug': r.get('slug', ''),
        })
    return sorted(result, key=lambda r: (r['timestamp'], r['record_id']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', action='store_true', help='Collect November-to-cutoff history for top-ranked wallets')
    args = parser.parse_args()
    cfg = read_json(ROOT / 'config.json')
    client = Client()
    coverage = []
    if args.history:
        with (ROOT / 'artifacts/ranking.csv').open(encoding='utf-8') as f:
            wallets = [r['wallet'] for r in list(csv.DictReader(f))[:cfg['history_top_n']]]
        summaries = []
        for n, wallet in enumerate(wallets, 1):
            rows = collect_windows(lambda p: client.get('https://data-api.polymarket.com/activity', p),
                {'user': wallet, 'type': 'TRADE', 'sortBy': 'TIMESTAMP', 'sortDirection': 'ASC'},
                epoch(cfg['lookback_start_utc']), epoch(cfg['cutoff_utc']) - 1, 500, coverage, wallet)
            normalized = normalize(rows)
            write_csv(ROOT / f'artifacts/history/{wallet}.csv', normalized)
            summaries.append({'wallet': wallet, 'rows': len(rows), 'first_observed_utc':
                min((r['utc'] for r in normalized), default=''),
                'markets': len(set(r['condition_id'] for r in normalized))})
            print(f'History {n}/{len(wallets)}: {wallet} {len(rows)} rows', flush=True)
        write_csv(ROOT / 'artifacts/history_coverage.csv', coverage)
        write_csv(ROOT / 'artifacts/history_summary.csv', summaries)
        return
    events = client.get('https://gamma-api.polymarket.com/events', {'slug': cfg['event_slug']})
    market = next(m for e in events for m in e['markets'] if m['id'] == cfg['market_id'])
    assert market['conditionId'] == cfg['condition_id']
    (ROOT / 'data/market.json').write_text(json.dumps(market, indent=2), encoding='utf-8')
    rows = collect_windows(lambda p: client.get('https://data-api.polymarket.com/trades', p),
        {'market': cfg['condition_id'], 'takerOnly': str(cfg['taker_only']).lower()},
        epoch(cfg['start_utc']), epoch(cfg['end_exclusive_utc']) - 1,
        cfg['page_limit'], coverage, cfg['market_id'])
    normalized = normalize(rows)
    write_csv(ROOT / 'artifacts/trades.csv', normalized)
    write_csv(ROOT / 'artifacts/coverage.csv', coverage)
    keys = Counter((r['transaction_hash'], r['wallet'], r['asset'], r['side'], r['size'], r['price']) for r in normalized)
    qa = {'rows': len(rows), 'wallets': len(set(r['wallet'] for r in normalized)),
          'transaction_hashes': len(set(r['transaction_hash'] for r in normalized)),
          'equal_economic_keys_beyond_first_retained': sum(v - 1 for v in keys.values()),
          'leaf_windows': len(coverage), 'first_utc': normalized[0]['utc'], 'last_utc': normalized[-1]['utc'],
          'taker_only': cfg['taker_only'], 'all_leaves_below_cap': True}
    (ROOT / 'artifacts/collection_qa.json').write_text(json.dumps(qa, indent=2), encoding='utf-8')
    print(json.dumps(qa, indent=2))


if __name__ == '__main__':
    main()
