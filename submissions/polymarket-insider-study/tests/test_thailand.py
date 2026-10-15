import csv
import gzip
import hashlib
import json
import sys
import unittest
import urllib.parse
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))
from collect import epoch, read_json
from analyze import load_trades
from thailand import check_transaction

ROOT = PROJECT / 'cases/thailand'


def signature(row, raw=False):
    return (int(row['timestamp']), row['proxyWallet' if raw else 'wallet'].lower(),
            row['asset'], row['side'], row['outcome'], float(row['size']),
            float(row['price']), row['transactionHash' if raw else 'transaction_hash'].lower())


class ThailandDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = read_json(ROOT / 'config.json')
        cls.rows = load_trades(ROOT / 'artifacts/trades.csv')

    def test_unchanged_score_and_cutoff_before_election_day_polling(self):
        original = read_json(PROJECT / 'config.json')
        for key in ['weights', 'minimum_recent_yes_buy_usdc', 'size_saturation_usdc', 'recent_hours', 'taker_only']:
            self.assertEqual(original[key], self.cfg[key])
        self.assertEqual(epoch(self.cfg['polls_open_utc']) - epoch(self.cfg['cutoff_utc']), 1800)

    def test_all_saved_api_responses_match_hashes(self):
        for line in (ROOT / 'data/request_manifest.jsonl').read_text().splitlines():
            entry = json.loads(line)
            with gzip.open(ROOT / entry['raw_file'], 'rb') as f:
                body = f.read()
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry['response_sha256'])

    def check_windows(self, rows, leaves, start, end, endpoint, params, limit):
        source = []
        expected = start
        for leaf in sorted(leaves, key=lambda x: x['start_utc']):
            a, b = epoch(leaf['start_utc']), epoch(leaf['end_inclusive_utc'])
            self.assertEqual(a, expected)
            self.assertLess(int(leaf['records']), limit)
            q = {**params, 'start': a, 'end': b, 'limit': limit, 'offset': 0}
            url = endpoint + '?' + urllib.parse.urlencode(sorted(q.items()))
            filename = hashlib.sha256(url.encode()).hexdigest() + '.json.gz'
            with gzip.open(ROOT / 'data/raw' / filename, 'rt', encoding='utf-8') as f:
                batch = json.load(f)
            self.assertEqual(len(batch), int(leaf['records']))
            self.assertTrue(all(a <= r['timestamp'] <= b for r in batch))
            source.extend(batch)
            expected = b + 1
        self.assertEqual(expected, end)
        self.assertEqual(Counter(signature(r, True) for r in source), Counter(signature(r) for r in rows))

    def test_market_download_exactly_matches_disjoint_source_windows(self):
        with (ROOT / 'artifacts/coverage.csv').open() as f:
            leaves = list(csv.DictReader(f))
        self.check_windows(self.rows, leaves, epoch(self.cfg['start_utc']), epoch(self.cfg['end_exclusive_utc']),
            'https://data-api.polymarket.com/trades', {'market': self.cfg['condition_id'], 'takerOnly': 'true'}, 1000)
        market = read_json(ROOT / 'data/market.json')
        mapping = dict(zip(json.loads(market['clobTokenIds']), json.loads(market['outcomes'])))
        for r in self.rows:
            self.assertEqual(r['condition_id'], self.cfg['condition_id'])
            self.assertEqual(r['outcome'], mapping[r['asset']])

    def test_complete_wallet_histories_match_source_windows(self):
        with (ROOT / 'artifacts/history_coverage.csv').open() as f:
            leaves = list(csv.DictReader(f))
        for wallet in self.cfg['full_history_wallets']:
            rows = load_trades(ROOT / f'artifacts/history/{wallet}.csv')
            self.assertTrue(all(r['wallet'] == wallet for r in rows))
            self.check_windows(rows, [l for l in leaves if l['scope'] == wallet],
                epoch(self.cfg['lookback_start_utc']), epoch(self.cfg['cutoff_utc']),
                'https://data-api.polymarket.com/activity',
                {'user': wallet, 'type': 'TRADE', 'sortBy': 'TIMESTAMP', 'sortDirection': 'ASC'}, 500)

    def test_chain_transfers_match_trade_and_reject_changed_amount(self):
        result = check_transaction(self.rows)
        self.assertTrue(result['api_match'])
        changed = [dict(r) for r in self.rows]
        for row in changed:
            if row['transaction_hash'] == result['transaction_hash']:
                row['notional_usdc'] += 1
        with self.assertRaisesRegex(ValueError, 'do not match'):
            check_transaction(changed)


if __name__ == '__main__':
    unittest.main()
