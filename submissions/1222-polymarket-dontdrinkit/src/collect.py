"""Collect core-market executions and bounded cross-market candidate history. Cache
exact public responses and SQL; record acquisition provenance.
"""

import argparse
import csv
import hashlib
import json
import ssl
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from prepare import data_path, load_metadata, save_metadata

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT


# Collect

HOST = 'https://crypto-clickhouse.clickhouse.com/'



class Client:
    def __init__(self, insecure=False):
        self.context = ssl._create_unverified_context() if insecure else ssl.create_default_context()
        self.insecure = insecure
        self.log = []

    def query(self, name, sql):
        rawdir = ROOT / 'data/source/raw'
        sqldir = ROOT / 'data/source/sql'
        rawdir.mkdir(exist_ok=True)
        sqldir.mkdir(exist_ok=True)
        rawpath = rawdir / f'{name}.json'
        sqlpath = sqldir / f'{name}.sql'
        if rawpath.exists():
            if not sqlpath.exists() or sqlpath.read_text(encoding='utf-8') != sql:
                raise ValueError(f'Cached query scope changed for {name}; use a new snapshot directory.')
            return json.loads(rawpath.read_text(encoding='utf-8'))
        sqlpath.write_text(sql, encoding='utf-8')
        url = HOST + '?' + urllib.parse.urlencode({'user': 'crypto', 'query': sql})
        req = urllib.request.Request(url, headers={'User-Agent': 'ScopedPolymarketResearch/1.0'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, context=self.context, timeout=120) as response:
                    body = response.read()
                    result = json.loads(body)
                if 'data' not in result:
                    raise ValueError('Missing data field')
                rawpath.write_bytes(body)
                self.log.append({'name': name, 'collected_at_utc': datetime.now(timezone.utc).isoformat(),
                                 'endpoint': HOST, 'sha256': hashlib.sha256(body).hexdigest(),
                                 'rows': result['rows'], 'tls_verified': not self.insecure,
                                 'statistics': result.get('statistics', {})})
                print(f'{name}: {result["rows"]} rows', flush=True)
                return result
            except urllib.error.HTTPError as error:
                message = error.read().decode('utf-8', errors='replace')
                if error.code in (400, 401, 403):
                    raise RuntimeError(f'HTTP {error.code}: {message[:3000]}') from error
                if attempt == 2:
                    raise RuntimeError(message[:3000]) from error
                time.sleep(2 ** attempt)
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)



def write_csv(name, rows):
    """Save a nonempty source table using its original field order."""
    output_path = data_path(name)
    output_path.parent.mkdir(exist_ok=True)
    if not rows:
        raise ValueError(f'No rows for {name}')
    with output_path.open('w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def collect(insecure=False):
    client = Client(insecure)
    config = json.loads((ROOT / 'config.json').read_text())
    server_timezone = client.query('server_timezone', 'SELECT timezone() AS timezone FORMAT JSON')
    assert server_timezone['data'][0]['timezone'] == 'UTC'
    token_ids = [t for m in config['markets'] for t in (m['yes_token'], m['no_token'])]
    token_sql = ','.join(f"'{t}'" for t in token_ids)
    start, end = config['collection_start'], config['collection_end']
    # timestamp and asset identity are stable per indexed fill; PREWHERE reduces
    # columns read before FINAL resolves the indexer's versioned rows.
    scope = (f"timestamp >= '{start}' AND timestamp < '{end}' AND "
             f"(maker_asset_id IN ({token_sql}) OR taker_asset_id IN ({token_sql}))")
    count = client.query('coverage_count', f"""SELECT count() AS n,
        uniqExact(id) AS unique_ids, min(timestamp) AS first, max(timestamp) AS last,
        countIf(maker_asset_id!='0' AND taker_asset_id!='0') AS noncash
        FROM polymarket.orders_filled FINAL PREWHERE {scope}
        WHERE is_deleted=0 FORMAT JSON""")['data'][0]
    expected = int(count['n'])
    fills, cursor = [], ''
    # Stable keyset pagination; no deduplication by transaction hash, since a
    # transaction may contain multiple different OrderFilled records.
    page = 0
    while len(fills) < expected:
        sql = f"""SELECT id, toUnixTimestamp(timestamp) AS timestamp_epoch,
          maker, taker, maker_asset_id, taker_asset_id,
          toString(maker_amount_filled) AS maker_amount_raw,
          toString(taker_amount_filled) AS taker_amount_raw,
          toString(fee) AS fee_raw, block_number
          FROM polymarket.orders_filled FINAL PREWHERE {scope}
          WHERE is_deleted=0 AND id > '{cursor}'
          ORDER BY id LIMIT 2000 FORMAT JSON"""
        result = client.query(f'fills_{page:03}', sql)
        rows = result['data']
        if not rows:
            break
        fills.extend(rows)
        cursor = rows[-1]['id']
        page += 1
    assert len(fills) == expected, (len(fills), expected)
    assert len({r['id'] for r in fills}) == expected
    assert int(count['unique_ids']) == expected
    write_csv('fills.csv', fills)
    write_csv('coverage.csv', [dict(source='CryptoHouse orders_filled', requested_start=start,
                                  requested_end_exclusive=end, **count)])
    mapping = client.query('token_mapping', f"""SELECT id AS token_id, complement,
        toString(condition) AS condition_id, outcome_index
        FROM polymarket.token_id_condition FINAL WHERE id IN ({token_sql})
        AND is_deleted=0 FORMAT JSON""")['data']
    write_csv('token_mapping.csv', mapping)
    actual = {r['token_id']: r for r in mapping}
    for m in config['markets']:
        assert int(actual[m['yes_token']]['outcome_index']) == 0
        assert actual[m['yes_token']]['complement'] == m['no_token']
        assert actual[m['yes_token']]['condition_id'] == m['condition_id']
    manifest = ROOT / 'data/provenance.json'
    saved_receipts = load_metadata('collection_manifest') if manifest.exists() else []
    save_metadata('collection_manifest', saved_receipts + client.log)
    snapshot_paths = [ROOT / 'data/source/raw' / f'fills_{page_number:03}.json' for page_number in range(page)]
    snapshot_paths.extend(ROOT / 'data/source/raw' / f'{name}.json' for name in ['coverage_count', 'token_mapping', 'server_timezone'])
    snapshot_paths.extend(ROOT / 'data/source/sql' / f'{path.stem}.sql' for path in list(snapshot_paths))
    snapshot = [dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in sorted(snapshot_paths)]
    save_metadata('snapshot_manifest', snapshot)
    return fills



# Collect history

def collect_history(inspect_only=False):
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    history_config = config['candidate_history']
    assert history_config['wallet_role'] == 'maker'
    assert history_config['market_scope'] == 'all_outcome_tokens'
    candidates = pd.read_csv(data_path('candidates.csv'))
    wallets = sorted(candidates['wallet'].tolist())
    assert len(wallets) == len(set(wallets))
    assert candidates['wallet'].str.fullmatch(r'0x[0-9a-f]{40}').all()
    history_start = pd.Timestamp(history_config['start_inclusive_utc'])
    history_end = pd.Timestamp(history_config['end_exclusive_utc'])
    start_sql = history_start.strftime('%Y-%m-%d %H:%M:%S')
    end_sql = history_end.strftime('%Y-%m-%d %H:%M:%S')
    wallet_sql = ','.join(f"'{wallet}'" for wallet in wallets)
    scope = f"timestamp >= '{start_sql}' AND timestamp < '{end_sql}'"
    wallet_filter = f"is_deleted=0 AND maker IN ({wallet_sql})"

    # Scope-specific cache names prevent reusing another pool or time interval.
    fingerprint = hashlib.sha256(json.dumps([wallets, start_sql, end_sql]).encode()).hexdigest()[:12]
    query_prefix = f'history_{fingerprint}'
    client = Client()
    query_names = []

    def query(suffix, sql):
        query_name = f'{query_prefix}_{suffix}'
        query_names.append(query_name)
        response = client.query(query_name, sql)
        if response.get('exception'):
            raise RuntimeError(f"Incomplete response for {query_name}: {response['exception']}")
        return response['data']

    timezone_rows = query('timezone', 'SELECT timezone() AS timezone FORMAT JSON')
    assert timezone_rows[0]['timezone'] == 'UTC'
    source_days = query('source_daily_bounds', f"""SELECT toDate(timestamp) AS day,
        count() AS fills, min(timestamp) AS first, max(timestamp) AS last
        FROM polymarket.orders_filled FINAL PREWHERE {scope}
        WHERE is_deleted=0 GROUP BY day ORDER BY day FORMAT JSON""")
    source_first = min(pd.Timestamp(row['first'], tz='UTC') for row in source_days)
    effective_baseline_start = pd.Timestamp(history_config['effective_baseline_start_inclusive_utc'])
    assert effective_baseline_start > source_first
    source_coverage = pd.DataFrame({'day': pd.date_range(history_start.floor('D'), history_end.floor('D'), freq='D').strftime('%Y-%m-%d')})
    source_coverage = source_coverage.merge(pd.DataFrame(source_days), on='day', how='left')
    source_coverage['fills'] = source_coverage['fills'].fillna(0).astype('int64')
    source_coverage['status'] = np.where(source_coverage['fills'] > 0, 'source_rows_observed', 'no_source_rows_in_requested_interval')
    counts = query('counts', f"""SELECT maker AS wallet, count() AS fills,
        uniqExact(id) AS unique_ids, min(timestamp) AS first, max(timestamp) AS last,
        countIf((maker_asset_id='0') != (taker_asset_id='0')) AS cash_outcome_fills
        FROM polymarket.orders_filled FINAL PREWHERE {scope}
        WHERE {wallet_filter} GROUP BY maker FORMAT JSON""")
    expected_count = sum(int(row['fills']) for row in counts)
    assert all(int(row['fills']) == int(row['unique_ids']) for row in counts)
    print(json.dumps({'wallets_requested': len(wallets), 'wallets_returned': len(counts),
                      'expected_fills': expected_count,
                      'largest_wallet_fills': max((int(row['fills']) for row in counts), default=0)}, indent=2), flush=True)
    if inspect_only:
        return

    daily_counts = query('daily_counts', f"""SELECT toDate(timestamp) AS day, count() AS fills
        FROM polymarket.orders_filled FINAL PREWHERE {scope}
        WHERE {wallet_filter} GROUP BY day ORDER BY day FORMAT JSON""")
    assert sum(int(row['fills']) for row in daily_counts) == expected_count

    def collect_day(day_count):
        # Disjoint days allow four independent requests at once and reduce
        # repeated scans. Pagination within each day remains sequential.
        day_start = max(history_start, pd.Timestamp(day_count['day'], tz='UTC'))
        day_end = min(history_end, pd.Timestamp(day_count['day'], tz='UTC') + pd.Timedelta(days=1))
        day_scope = f"timestamp >= '{day_start.strftime('%Y-%m-%d %H:%M:%S')}' AND timestamp < '{day_end.strftime('%Y-%m-%d %H:%M:%S')}'"
        day_rows = []
        cursor = ''
        page_number = 0
        while len(day_rows) < int(day_count['fills']):
            suffix = f"day_{day_count['day']}_fills_{history_config['page_size']}_{page_number:04}"
            rows = query(suffix, f"""SELECT id,
                toUnixTimestamp(timestamp) AS timestamp_epoch, maker, taker,
                maker_asset_id, taker_asset_id,
                toString(maker_amount_filled) AS maker_amount_raw,
                toString(taker_amount_filled) AS taker_amount_raw,
                toString(fee) AS fee_raw, block_number
                FROM polymarket.orders_filled FINAL PREWHERE {day_scope}
                WHERE {wallet_filter} AND id > '{cursor}'
                ORDER BY id LIMIT {history_config['page_size']} FORMAT JSON""")
            if not rows:
                break
            assert len(rows) <= history_config['page_size']
            assert [row['id'] for row in rows] == sorted(row['id'] for row in rows)
            assert rows[0]['id'] > cursor
            day_rows.extend(rows)
            cursor = rows[-1]['id']
            page_number += 1
        assert len(day_rows) == int(day_count['fills']), day_count['day']
        return day_rows

    raw_rows = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for day_rows in executor.map(collect_day, daily_counts):
            raw_rows.extend(day_rows)

    raw_fills = pd.DataFrame(raw_rows).astype(str)
    assert len(raw_fills) == expected_count
    assert raw_fills['id'].is_unique
    actual_counts = raw_fills.groupby('maker').size().to_dict()
    assert actual_counts == {row['wallet']: int(row['fills']) for row in counts}
    timestamps = pd.to_datetime(raw_fills['timestamp_epoch'].astype('int64'), unit='s', utc=True)
    assert timestamps.ge(history_start).all() and timestamps.lt(history_end).all()
    assert set(raw_fills['maker']) <= set(wallets)
    for row in counts:
        wallet_times = timestamps[raw_fills['maker'] == row['wallet']]
        assert wallet_times.min() == pd.Timestamp(row['first'], tz='UTC')
        assert wallet_times.max() == pd.Timestamp(row['last'], tz='UTC')

    # Retain unsupported asset pairs in raw history, but do not invent cash
    # values or directions for them in the normalized cash/outcome table.
    is_cash_pair = raw_fills['maker_asset_id'].eq('0') ^ raw_fills['taker_asset_id'].eq('0')
    assert int(is_cash_pair.sum()) == sum(int(row['cash_outcome_fills']) for row in counts)
    history_trades = raw_fills[is_cash_pair].copy()
    is_buy = history_trades['maker_asset_id'].eq('0')
    history_trades['wallet'] = history_trades['maker'].str.lower()
    history_trades['token_id'] = history_trades['taker_asset_id'].where(is_buy, history_trades['maker_asset_id'])
    history_trades['side'] = np.where(is_buy, 'BUY', 'SELL')
    history_trades['cash'] = pd.to_numeric(history_trades['maker_amount_raw'].where(is_buy, history_trades['taker_amount_raw'])) / 1_000_000
    history_trades['shares'] = pd.to_numeric(history_trades['taker_amount_raw'].where(is_buy, history_trades['maker_amount_raw'])) / 1_000_000
    history_trades['price'] = history_trades['cash'] / history_trades['shares']
    history_trades['fee'] = pd.to_numeric(history_trades['fee_raw']) / 1_000_000
    history_trades['timestamp_utc'] = timestamps[is_cash_pair]
    assert history_trades['price'].between(0, 1.00001).all()
    assert history_trades['shares'].gt(0).all()

    # Condition IDs group complementary YES/NO tokens into one market. Market
    # titles are unnecessary for concentration and purchase-volume baselines.
    token_ids = sorted(history_trades['token_id'].unique())
    token_rows = []
    for batch_start in range(0, len(token_ids), 400):
        token_sql = ','.join(f"'{token_id}'" for token_id in token_ids[batch_start:batch_start + 400])
        token_rows.extend(query(f'tokens_{batch_start // 400:04}', f"""SELECT id AS token_id,
            complement, toString(condition) AS condition_id, outcome_index
            FROM polymarket.token_id_condition FINAL
            WHERE is_deleted=0 AND id IN ({token_sql}) FORMAT JSON"""))
    token_mapping = pd.DataFrame(token_rows).astype(str)
    assert token_mapping['token_id'].is_unique
    condition_by_token = token_mapping.set_index('token_id')['condition_id']
    outcome_index_by_token = token_mapping.set_index('token_id')['outcome_index']
    history_trades['condition_id'] = history_trades['token_id'].map(condition_by_token)
    history_trades['outcome_index'] = history_trades['token_id'].map(outcome_index_by_token)

    # The main baseline excludes the entire screening window. The extra hour
    # supports the late-cutoff scenario only, never the main pre-cutoff score.
    baseline_end = pd.Timestamp(history_config['main_baseline_end_exclusive_utc'])
    main_cutoff = pd.Timestamp(config['analysis_cutoff'])
    coverage = pd.DataFrame({'wallet': wallets}).set_index('wallet')
    coverage['history_fills'] = pd.Series(actual_counts).reindex(wallets, fill_value=0)
    for label, subset in [
        ('cash_outcome', history_trades),
        ('baseline', history_trades[(history_trades['timestamp_utc'] >= effective_baseline_start) & (history_trades['timestamp_utc'] < baseline_end)]),
        ('baseline_buy', history_trades[(history_trades['timestamp_utc'] >= effective_baseline_start) & (history_trades['timestamp_utc'] < baseline_end) & (history_trades['side'] == 'BUY')]),
        ('main_recent', history_trades[(history_trades['timestamp_utc'] >= baseline_end) & (history_trades['timestamp_utc'] < main_cutoff)]),
    ]:
        coverage[f'{label}_fills'] = subset.groupby('wallet').size().reindex(wallets, fill_value=0)
    baseline_trades = history_trades[(history_trades['timestamp_utc'] >= effective_baseline_start) & (history_trades['timestamp_utc'] < baseline_end)]
    # Align 24-hour bins with the 05:00 UTC window boundary.
    baseline_days = (baseline_trades['timestamp_utc'] - effective_baseline_start).dt.total_seconds() // 86400
    coverage['baseline_active_days'] = baseline_trades.assign(day=baseline_days).groupby('wallet')['day'].nunique().reindex(wallets, fill_value=0)
    coverage['baseline_markets'] = baseline_trades.groupby('wallet')['condition_id'].nunique().reindex(wallets, fill_value=0)
    coverage['unmapped_fills'] = history_trades[history_trades['condition_id'].isna()].groupby('wallet').size().reindex(wallets, fill_value=0)
    coverage['history_status'] = np.where(coverage['baseline_fills'] > 0, 'baseline_observed', 'no_baseline_fills_in_interval')

    raw_fills.to_csv(data_path('history_fills.csv'), index=False)
    history_trades.to_csv(data_path('history_trades.csv'), index=False)
    token_mapping.to_csv(data_path('history_token_mapping.csv'), index=False)
    coverage.reset_index().to_csv(data_path('history_coverage.csv'), index=False)
    source_coverage.to_csv(data_path('history_source_coverage.csv'), index=False)
    snapshot_files = []
    for name in query_names:
        for directory, extension in [('raw', 'json'), ('sql', 'sql')]:
            path = PROJECT_ROOT / 'data/source' / directory / f'{name}.{extension}'
            snapshot_files.append({'path': path.relative_to(PROJECT_ROOT).as_posix(),
                                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'bytes': path.stat().st_size,
                                   'saved_file_modified_at_utc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()})
    manifest_path = PROJECT_ROOT / 'data/provenance.json'
    saved_manifest = load_metadata('history_manifest') if manifest_path.exists() else {}
    pool_hash = hashlib.sha256((data_path('candidates.csv')).read_bytes()).hexdigest()
    saved_requests = []
    if (saved_manifest.get('pool_sha256') == pool_hash and
            saved_manifest.get('start_inclusive_utc') == history_start.isoformat() and
            saved_manifest.get('end_exclusive_utc') == history_end.isoformat()):
        saved_requests = saved_manifest.get('request_log', [])
    report = {
        'status': 'complete', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'endpoint': 'https://crypto-clickhouse.clickhouse.com/', 'tls_verified': True,
        'pool_sha256': pool_hash,
        'start_inclusive_utc': history_start.isoformat(), 'end_exclusive_utc': history_end.isoformat(),
        'main_baseline_end_exclusive_utc': baseline_end.isoformat(),
        'effective_baseline_start_inclusive_utc': effective_baseline_start.isoformat(),
        'effective_main_baseline_days': (baseline_end - effective_baseline_start).total_seconds() / 86400,
        'first_source_fill_in_requested_interval': source_first.isoformat(),
        'source_days_without_rows': source_coverage.loc[source_coverage['fills'] == 0, 'day'].tolist(),
        'requested_wallets': len(wallets), 'wallets_with_history': len(actual_counts),
        'wallets_with_baseline': int(coverage['baseline_fills'].gt(0).sum()),
        'wallets_without_baseline': int(coverage['baseline_fills'].eq(0).sum()),
        'raw_fills': len(raw_fills), 'normalized_cash_outcome_fills': len(history_trades),
        'unsupported_pair_fills': int((~is_cash_pair).sum()),
        'tokens_requested': len(token_ids), 'tokens_mapped': len(token_mapping),
        'unmapped_fills': int(history_trades['condition_id'].isna().sum()),
        'post_main_cutoff_fills': int(history_trades['timestamp_utc'].ge(main_cutoff).sum()),
        'queries': snapshot_files, 'request_log': saved_requests + client.log,
        'limitations': [
            'Bounded maker history from a public mirror, not lifetime or independently verified chain completeness.',
            'The source has no rows before December 18 in the requested interval; those days are not zero-activity baseline days.',
            'No baseline fills means no activity observed in this interval, not a new wallet.',
            'All metrics must apply their scenario cutoff; the last hour is not a main-score input.',
            'Unmapped tokens cannot be treated as distinct confirmed markets.',
        ],
    }
    save_metadata('history_manifest', report)
    print(json.dumps({key: value for key, value in report.items() if key not in ['queries', 'request_log']}, indent=2))

