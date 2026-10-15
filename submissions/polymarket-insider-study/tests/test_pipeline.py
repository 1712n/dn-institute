import copy
import csv
import gzip
import hashlib
import json
import math
import sys
import tempfile
import unittest
import urllib.parse
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from collect import collect_windows, epoch, read_json
from analyze import rank, load_trades
import collect


class CollectionTests(unittest.TestCase):
    def test_metadata_mismatch_stops_before_saving_or_collecting_trades(self):
        cfg = read_json(ROOT / 'config.json')
        events = [{'markets': [{'id': cfg['market_id'], 'conditionId': 'wrong'}]}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            with (patch.object(collect, 'ROOT', root),
                  patch.object(collect, 'read_json', return_value=cfg),
                  patch.object(collect, 'Client') as client,
                  patch.object(sys, 'argv', ['collect.py'])):
                client.return_value.get.return_value = events
                with self.assertRaisesRegex(ValueError, 'Market condition ID does not match config'):
                    collect.main()
                self.assertEqual(client.return_value.get.call_count, 1)
                self.assertFalse((root / 'data/market.json').exists())

    def test_splitting_has_no_gaps_or_duplicate_boundaries(self):
        source = [{'timestamp': t} for t in range(13)]
        def fetch(p):
            return [r for r in source if p['start'] <= r['timestamp'] <= p['end']][:p['limit']]
        coverage = []
        actual = collect_windows(fetch, {}, 0, 12, 4, coverage, 'test')
        self.assertEqual(actual, source)
        self.assertTrue(all(r['records'] < 4 for r in coverage))

    def test_exact_limit_is_split_not_assumed_complete(self):
        calls = []
        def fetch(p):
            calls.append(p)
            return [{'timestamp': t} for t in range(4) if p['start'] <= t <= p['end']][:4]
        self.assertEqual(len(collect_windows(fetch, {}, 0, 3, 4, [], 'test')), 4)
        self.assertGreater(len(calls), 1)

    def test_saturated_second_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'Saturated'):
            collect_windows(lambda p: [{'timestamp': 1}] * 3, {}, 1, 1, 3, [], 'test')

    def test_ignored_date_filter_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'timestamp'):
            collect_windows(lambda p: [{'timestamp': 99}], {}, 0, 10, 3, [], 'test')

    def test_wrong_market_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'market'):
            collect_windows(lambda p: [{'timestamp': 1, 'conditionId': 'wrong'}],
                            {'market': 'expected'}, 0, 10, 3, [], 'test')

    def test_duplicate_valued_fills_are_not_dropped(self):
        rows = [{'timestamp': 1}, {'timestamp': 1}]
        self.assertEqual(collect_windows(lambda p: rows, {}, 0, 10, 3, [], 'test'), rows)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.cfg = read_json(ROOT / 'config.json')
        self.cut = 200000

    def row(self, timestamp=None, cash=1000, price=0.1, side='BUY', outcome='Yes', wallet='A'):
        return {'timestamp': self.cut - 1 if timestamp is None else timestamp,
                'wallet': wallet, 'notional_usdc': cash, 'size': cash/price,
                'side': side, 'outcome': outcome, 'price': price}

    def test_cutoff_is_exclusive(self):
        rows = [self.row(), self.row(timestamp=self.cut, cash=1e9)]
        r = rank(rows, self.cut, self.cfg)[0]
        self.assertEqual(r['recent_yes_buy_usdc'], 1000)
        self.assertEqual(r['pre_cutoff_records'], 1)

    def test_lower_boundary_is_inclusive(self):
        rows = [self.row(timestamp=self.cut-86400), self.row(timestamp=self.cut-86401)]
        r = rank(rows, self.cut, self.cfg)[0]
        self.assertEqual(r['recent_yes_buy_usdc'], 1000)
        self.assertEqual(r['recency_feature'], 0.5)

    def test_minimum_exposure_gate(self):
        self.assertEqual(rank([self.row(cash=499)], self.cut, self.cfg)[0]['score'], 0)
        self.assertGreater(rank([self.row(cash=500)], self.cut, self.cfg)[0]['score'], 0)

    def test_opposite_side_and_sales_reduce_one_sidedness(self):
        baseline = rank([self.row()], self.cut, self.cfg)[0]
        hedged = rank([self.row(), self.row(outcome='No'), self.row(side='SELL')], self.cut, self.cfg)[0]
        self.assertAlmostEqual(hedged['direction_feature'], 1/3)
        self.assertLess(hedged['score'], baseline['score'])

    def test_hand_calculated_full_score(self):
        r = rank([self.row(cash=10000, price=0.1)], self.cut, self.cfg)[0]
        self.assertAlmostEqual(r['score'], 30 + 25 + 20 + 25 * 0.9)
        self.assertAlmostEqual(r['buy_and_hold_upside_scenario_usdc'], 90000)

    def test_post_event_and_input_order_do_not_change_ranking(self):
        rows = [self.row(wallet='B'), self.row(wallet='A')]
        rr = rank(rows, self.cut, self.cfg)
        self.assertEqual(rr, rank(list(reversed(rows)) + [self.row(timestamp=self.cut+10)], self.cut, self.cfg))


class FrozenDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = read_json(ROOT / 'config.json')
        cls.rows = load_trades(ROOT / 'artifacts/trades.csv')

    def test_leaf_coverage_is_contiguous_and_exhausted(self):
        with (ROOT / 'artifacts/coverage.csv').open() as f:
            leaves = list(csv.DictReader(f))
        leaves.sort(key=lambda r: r['start_utc'])
        expected = epoch(self.cfg['start_utc'])
        count = 0
        for leaf in leaves:
            self.assertEqual(epoch(leaf['start_utc']), expected)
            expected = epoch(leaf['end_inclusive_utc']) + 1
            self.assertLess(int(leaf['records']), int(leaf['limit']))
            count += int(leaf['records'])
        self.assertEqual(expected, epoch(self.cfg['end_exclusive_utc']))
        self.assertEqual(count, len(self.rows))

    def test_token_outcome_mapping_and_notional(self):
        market = read_json(ROOT / 'data/market.json')
        mapping = dict(zip(json.loads(market['clobTokenIds']), json.loads(market['outcomes'])))
        for r in self.rows:
            self.assertEqual(r['outcome'], mapping[r['asset']])
            self.assertEqual(r['condition_id'], self.cfg['condition_id'])
            self.assertAlmostEqual(r['notional_usdc'], r['size']*r['price'], places=8)

    def test_frozen_responses_match_manifest_hashes(self):
        for line in (ROOT / 'data/request_manifest.jsonl').read_text().splitlines():
            entry = json.loads(line)
            with gzip.open(ROOT / entry['raw_file'], 'rb') as f:
                body = f.read()
            self.assertEqual(hashlib.sha256(body).hexdigest(), entry['response_sha256'])

    def test_csv_is_exactly_the_union_of_uncapped_source_windows(self):
        with (ROOT / 'artifacts/coverage.csv').open() as f:
            leaves = list(csv.DictReader(f))
        source = []
        for leaf in leaves:
            params = {'market': self.cfg['condition_id'], 'takerOnly': 'true',
                      'start': epoch(leaf['start_utc']), 'end': epoch(leaf['end_inclusive_utc']),
                      'limit': self.cfg['page_limit'], 'offset': 0}
            url = 'https://data-api.polymarket.com/trades?' + urllib.parse.urlencode(sorted(params.items()))
            key = hashlib.sha256(url.encode()).hexdigest()
            with gzip.open(ROOT / f'data/raw/{key}.json.gz', 'rt', encoding='utf-8') as f:
                source.extend(json.load(f))
        expected = Counter((r['timestamp'], r['proxyWallet'].lower(), r['asset'], r['side'],
                            r['outcome'], float(r['size']), float(r['price']), r['transactionHash'].lower()) for r in source)
        actual = Counter((r['timestamp'], r['wallet'], r['asset'], r['side'],
                          r['outcome'], r['size'], r['price'], r['transaction_hash']) for r in self.rows)
        self.assertEqual(expected, actual)

    def test_score_bounds_and_component_reconciliation(self):
        rr = rank(self.rows, epoch(self.cfg['cutoff_utc']), self.cfg)
        for r in rr:
            self.assertTrue(0 <= r['score'] <= 100)
            self.assertAlmostEqual(r['score'], sum(r[k+'_points'] for k in self.cfg['weights']))
            self.assertTrue(math.isfinite(r['score']))

    def test_wallet_histories_have_exhausted_contiguous_coverage(self):
        with (ROOT / 'artifacts/history_coverage.csv').open() as f:
            leaves = list(csv.DictReader(f))
        for wallet in sorted(set(r['scope'] for r in leaves)):
            windows = sorted((r for r in leaves if r['scope'] == wallet), key=lambda r: r['start_utc'])
            expected = epoch(self.cfg['lookback_start_utc'])
            count = 0
            for leaf in windows:
                self.assertEqual(epoch(leaf['start_utc']), expected)
                self.assertLess(int(leaf['records']), int(leaf['limit']))
                expected = epoch(leaf['end_inclusive_utc']) + 1
                count += int(leaf['records'])
            self.assertEqual(expected, epoch(self.cfg['cutoff_utc']))
            history = load_trades(ROOT / f'artifacts/history/{wallet}.csv')
            self.assertEqual(count, len(history))
            self.assertTrue(all(r['wallet'] == wallet and epoch(self.cfg['lookback_start_utc']) <=
                                r['timestamp'] < expected for r in history))


if __name__ == '__main__':
    unittest.main()
