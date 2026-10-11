"""Verify source coverage, normalization, history, metrics, ranking and sensitivity.
Preserve stage-level checks and write outcomes to the consolidated run log.
"""

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import math
from prepare import data_path, load_metadata, save_metadata, normalize_trades, screening_totals
from metrics import calculate_metrics, METRIC_COLUMNS
from ranking import rank_candidates, scenario_definitions

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT


# Audit coverage

def audit_coverage():
    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8-sig"))
    collection_start = datetime.fromisoformat(config["collection_start"]).replace(tzinfo=timezone.utc)
    collection_end = datetime.fromisoformat(config["collection_end"]).replace(tzinfo=timezone.utc)
    analysis_cutoff = datetime.fromisoformat(config["analysis_cutoff"])

    token_mapping = {}
    for market in config["markets"]:
        token_mapping[market["yes_token"]] = (market["key"], "YES")
        token_mapping[market["no_token"]] = (market["key"], "NO")

    # Check the saved snapshot, without claiming a new independent collection.
    snapshot_manifest = load_metadata('snapshot_manifest')
    for entry in snapshot_manifest:
        source_path = PROJECT_ROOT / entry["path"]
        actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_hash != entry["sha256"]:
            raise ValueError(f"Snapshot hash mismatch: {entry['path']}")

    with (data_path("fills.csv")).open(encoding="utf-8", newline="") as source_file:
        saved_fills = list(csv.DictReader(source_file))

    raw_fills_by_id = {}
    raw_page_paths = sorted((PROJECT_ROOT / "data/source/raw").glob("fills_*.json"))
    for page_path in raw_page_paths:
        page = json.loads(page_path.read_text(encoding="utf-8"))
        for raw_fill in page["data"]:
            if raw_fill["id"] in raw_fills_by_id:
                raise ValueError(f"Duplicate raw fill ID in {page_path.name}")
            raw_fills_by_id[raw_fill["id"]] = raw_fill

    coverage_response = json.loads(
        (PROJECT_ROOT / 'data/source/raw/coverage_count.json').read_text(encoding='utf-8')
    )["data"][0]
    expected_count = int(coverage_response["n"])
    provenance = json.loads((PROJECT_ROOT / 'data/provenance.json').read_text(encoding='utf-8'))
    projection = provenance.get('scope_projection')
    if projection:
        assert projection['selected_rows'] == expected_count
        assert set(projection['selected_tokens']) == set(token_mapping)
        for path in raw_page_paths:
            assert json.loads(path.read_text(encoding='utf-8'))['origin_kind'] == 'filtered_saved_snapshot'
    saved_ids = {fill["id"] for fill in saved_fills}
    if not (
        len(saved_fills) == len(saved_ids) == len(raw_fills_by_id)
        == expected_count == int(coverage_response["unique_ids"])
        and saved_ids == set(raw_fills_by_id)
    ):
        raise ValueError("Saved fills do not reconcile with the raw pages and coverage response")

    daily_counts = Counter()
    daily_wallets = defaultdict(set)
    core_fill_times = []
    all_fill_times = []
    for fill in saved_fills:
        raw_fill = raw_fills_by_id[fill["id"]]
        if any(str(raw_fill[column]) != value for column, value in fill.items()):
            raise ValueError(f"Saved fields differ from raw response: {fill['id']}")

        timestamp = datetime.fromtimestamp(int(fill["timestamp_epoch"]), tz=timezone.utc)
        if not collection_start <= timestamp < collection_end:
            raise ValueError(f"Fill outside requested collection interval: {fill['id']}")

        maker_pays_collateral = fill["maker_asset_id"] == "0"
        taker_pays_collateral = fill["taker_asset_id"] == "0"
        if maker_pays_collateral == taker_pays_collateral:
            raise ValueError(f"Unexpected asset pair: {fill['id']}")

        token_id = fill["taker_asset_id"] if maker_pays_collateral else fill["maker_asset_id"]
        market_name, outcome = token_mapping[token_id]
        side = "BUY" if maker_pays_collateral else "SELL"
        daily_key = (timestamp.date().isoformat(), market_name, outcome, side)
        daily_counts[daily_key] += 1
        daily_wallets[daily_key].add(fill["maker"].lower())
        all_fill_times.append(timestamp)
        if market_name == config["markets"][0]["key"]:
            core_fill_times.append((timestamp, fill["maker"].lower()))

    source_first = datetime.fromisoformat(coverage_response["first"]).replace(tzinfo=timezone.utc)
    source_last = datetime.fromisoformat(coverage_response["last"]).replace(tzinfo=timezone.utc)
    if min(all_fill_times) != source_first or max(all_fill_times) != source_last:
        raise ValueError("Saved timestamp bounds differ from the coverage response")

    daily_rows = []
    collection_day = collection_start.date()
    while collection_day < collection_end.date():
        for market in config["markets"]:
            for outcome in ("YES", "NO"):
                for side in ("BUY", "SELL"):
                    daily_key = (collection_day.isoformat(), market["key"], outcome, side)
                    daily_rows.append({
                        "date_utc": daily_key[0],
                        "market": market["key"],
                        "outcome": outcome,
                        "side": side,
                        "fills": daily_counts[daily_key],
                        "wallets": len(daily_wallets[daily_key]),
                    })
        collection_day += timedelta(days=1)

    with (data_path("daily_coverage.csv")).open(
        "w", encoding="utf-8", newline=""
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(daily_rows[0]))
        writer.writeheader()
        writer.writerows(daily_rows)

    window_coverage = []
    for window_hours in config["data_preparation"]["coverage_review_windows_hours"]:
        window_start = analysis_cutoff - timedelta(hours=window_hours)
        window_fills = [
            (timestamp, wallet) for timestamp, wallet in core_fill_times
            if window_start <= timestamp < analysis_cutoff
        ]
        window_coverage.append({
            "window_hours": window_hours,
            "start_inclusive": window_start.isoformat(),
            "end_exclusive": analysis_cutoff.isoformat(),
            "covered_by_requested_interval": window_start >= collection_start,
            "fills": len(window_fills),
            "wallets": len({wallet for _, wallet in window_fills}),
        })

    summary = {
        "status": "saved_snapshot_reconciled",
        "fresh_network_collection": False,
        "snapshot_origin": 'filtered_saved_snapshot' if projection else 'saved_source_responses',
        "requested_start_inclusive": collection_start.isoformat(),
        "requested_end_exclusive": collection_end.isoformat(),
        "observed_first_fill": min(all_fill_times).isoformat(),
        "observed_last_fill": max(all_fill_times).isoformat(),
        "saved_fills": len(saved_fills),
        "raw_pages": len(raw_page_paths),
        "verified_snapshot_files": len(snapshot_manifest),
        "core_wallets_before_cutoff": len({
            wallet for timestamp, wallet in core_fill_times if timestamp < analysis_cutoff
        }),
        "window_coverage": window_coverage,
        "limitations": [
            "Reconciliation establishes consistency within the saved mirror scope, not chain completeness.",
            "Scope projection, when present, filters a prior saved snapshot and is not a new source count query.",
            "Zero daily rows mean no fills in this snapshot; they do not independently prove absence of activity.",
        ],
    }
    save_metadata('coverage_audit', json.loads(json.dumps(summary, indent=2) + "\n"))
    print(json.dumps(summary, indent=2))



# Verify normalization

def verify_normalization():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    raw_fills = pd.read_csv(data_path('fills.csv'), dtype=str)
    trades = normalize_trades(raw_fills, config['markets'])

    # Recompute normalized values directly from raw fills and compare with
    # the saved table, allowing only floating-point CSV round-off.
    saved_trades = pd.read_csv(
        data_path('trades.csv'),
        dtype={column: str for column in raw_fills.columns} | {'token_id': str},
    )
    saved_trades['timestamp_utc'] = pd.to_datetime(saved_trades['timestamp_utc'], utc=True)
    pd.testing.assert_frame_equal(
        trades, saved_trades, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12
    )

    # Independently recover gross cash and shares from integer source amounts.
    expected_cash = []
    expected_shares = []
    for fill in raw_fills.itertuples(index=False):
        if fill.maker_asset_id == '0':
            expected_cash.append(int(fill.maker_amount_raw) / 1_000_000)
            expected_shares.append(int(fill.taker_amount_raw) / 1_000_000)
        else:
            expected_cash.append(int(fill.taker_amount_raw) / 1_000_000)
            expected_shares.append(int(fill.maker_amount_raw) / 1_000_000)
    np.testing.assert_allclose(trades['cash'], expected_cash, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(trades['shares'], expected_shares, rtol=1e-12, atol=1e-12)

    # Four explicit cases cover both directions of both outcomes. All share
    # one transaction and wallet, so collapsing those keys would fail here.
    fixture_market = [{'key': 'example_market', 'yes_token': '101', 'no_token': '102'}]
    transaction_hash = '0x' + 'a' * 64
    maker_address = '0x' + 'B' * 40
    fixture_rows = []
    for execution_index, (maker_asset, taker_asset, maker_amount, taker_amount) in enumerate([
        ('0', '101', '4000000', '10000000'),
        ('101', '0', '10000000', '6000000'),
        ('0', '102', '6000000', '10000000'),
        ('102', '0', '10000000', '4000000'),
    ]):
        fixture_rows.append({
            'id': f'{transaction_hash}_{execution_index}',
            'timestamp_epoch': '1767412800',
            'maker': maker_address,
            'taker': '0x' + 'c' * 40,
            'maker_asset_id': maker_asset,
            'taker_asset_id': taker_asset,
            'maker_amount_raw': maker_amount,
            'taker_amount_raw': taker_amount,
            'fee_raw': '100000',
            'block_number': '1',
        })
    fixture_trades = normalize_trades(pd.DataFrame(fixture_rows), fixture_market)
    assert fixture_trades['side'].tolist() == ['BUY', 'SELL', 'BUY', 'SELL']
    assert fixture_trades['outcome'].tolist() == ['Yes', 'Yes', 'No', 'No']
    assert fixture_trades['cash'].tolist() == [4.0, 6.0, 6.0, 4.0]
    assert fixture_trades['shares'].tolist() == [10.0] * 4
    assert fixture_trades['price'].tolist() == [0.4, 0.6, 0.6, 0.4]
    assert fixture_trades['fee'].tolist() == [0.1] * 4
    assert fixture_trades['wallet'].tolist() == [maker_address.lower()] * 4
    assert fixture_trades['timestamp_utc'].eq(pd.Timestamp('2026-01-03T04:00:00Z')).all()
    assert len(fixture_trades) == 4 and fixture_trades['tx_hash'].nunique() == 1

    # Unsupported asset pairs must fail instead of acquiring a guessed side.
    for maker_asset, taker_asset in [('0', '0'), ('101', '102')]:
        invalid_fills = pd.DataFrame([fixture_rows[0]])
        invalid_fills.loc[0, ['maker_asset_id', 'taker_asset_id']] = [maker_asset, taker_asset]
        try:
            normalize_trades(invalid_fills, fixture_market)
        except AssertionError:
            pass
        else:
            raise AssertionError('Unsupported asset pair was accepted')

    report = {
        'status': 'passed',
        'normalized_rows': len(trades),
        'saved_trades_reproduced_from_raw': True,
        'checks': [
            'all saved trade columns reproduce from raw fills',
            'integer source amounts independently reproduce cash and shares',
            'YES BUY, YES SELL, NO BUY, NO SELL synthetic cases',
            'six-decimal amounts, separate gross cash and fee, UTC timestamp',
            'maker ownership and lowercase wallet addresses',
            'multiple executions in one transaction remain separate',
            'cash/cash and outcome/outcome pairs are rejected',
        ],
        'fills_by_outcome_and_side': trades.groupby(['outcome', 'side']).size().rename('fills').reset_index().to_dict('records'),
    }
    save_metadata('normalization_audit', report)
    print(json.dumps(report, indent=2))



# Verify history

def verify_history():
    manifest = load_metadata('history_manifest')
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    assert hashlib.sha256((data_path('candidates.csv')).read_bytes()).hexdigest() == manifest['pool_sha256']
    raw_history = pd.read_csv(data_path('history_fills.csv'), dtype=str)
    assert raw_history['id'].is_unique
    raw_index = raw_history.set_index('id')
    source_ids = set()
    page_rows = 0
    for entry in manifest['queries']:
        source_path = PROJECT_ROOT / entry['path']
        assert hashlib.sha256(source_path.read_bytes()).hexdigest() == entry['sha256'], entry['path']
        if source_path.suffix == '.json':
            response = json.loads(source_path.read_text(encoding='utf-8'))
            assert not response.get('exception'), entry['path']
            if '_fills_' in source_path.name:
                page_frame = pd.DataFrame(response['data']).astype(str).set_index('id')
                pd.testing.assert_frame_equal(page_frame, raw_index.loc[page_frame.index])
                for fill in response['data']:
                    assert fill['id'] not in source_ids
                    source_ids.add(fill['id'])
                page_rows += len(response['data'])
    assert source_ids == set(raw_history['id'])
    assert page_rows == len(raw_history) == manifest['raw_fills']

    history = pd.read_csv(data_path('history_trades.csv'), dtype={
        'token_id': str, 'maker_asset_id': str, 'taker_asset_id': str,
    })
    history['timestamp_utc'] = pd.to_datetime(history['timestamp_utc'], utc=True)
    supported = raw_history['maker_asset_id'].eq('0') ^ raw_history['taker_asset_id'].eq('0')
    assert set(history['id']) == set(raw_history.loc[supported, 'id'])
    assert history['timestamp_utc'].ge(pd.Timestamp(manifest['start_inclusive_utc'])).all()
    assert history['timestamp_utc'].lt(pd.Timestamp(manifest['end_exclusive_utc'])).all()
    assert (history['wallet'] == history['maker'].str.lower()).all()
    assert (history['side'].eq('BUY') == history['maker_asset_id'].eq('0')).all()
    assert (history['side'].eq('SELL') == history['taker_asset_id'].eq('0')).all()
    normalized_index = history.set_index('id')
    for side, cash_column, shares_column in [
        ('BUY', 'maker_amount_raw', 'taker_amount_raw'),
        ('SELL', 'taker_amount_raw', 'maker_amount_raw'),
    ]:
        side_trades = normalized_index[normalized_index['side'] == side]
        source = raw_index.loc[side_trades.index]
        np.testing.assert_allclose(side_trades['cash'], pd.to_numeric(source[cash_column]) / 1_000_000)
        np.testing.assert_allclose(side_trades['shares'], pd.to_numeric(source[shares_column]) / 1_000_000)
    np.testing.assert_allclose(history['price'] * history['shares'], history['cash'])

    # Every scoped source fill for a candidate before the main cutoff must
    # appear unchanged in the cross-market historical collection.
    candidates = pd.read_csv(data_path('candidates.csv'))
    scoped = pd.read_csv(data_path('trades.csv'), dtype={
        'token_id': str, 'maker_asset_id': str, 'taker_asset_id': str,
    })
    scoped['timestamp_utc'] = pd.to_datetime(scoped['timestamp_utc'], utc=True)
    scoped = scoped[scoped['wallet'].isin(candidates['wallet']) & (scoped['timestamp_utc'] < pd.Timestamp(config['analysis_cutoff']))]
    assert set(scoped['id']) <= set(history['id'])
    common_columns = ['wallet', 'token_id', 'side', 'cash', 'shares', 'price', 'fee', 'timestamp_utc']
    pd.testing.assert_frame_equal(
        scoped.set_index('id')[common_columns].sort_index(),
        normalized_index.loc[scoped['id'], common_columns].sort_index(),
        check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12,
    )

    coverage = pd.read_csv(data_path('history_coverage.csv')).set_index('wallet')
    assert set(coverage.index) == set(candidates['wallet'])
    assert coverage['history_fills'].sum() == len(raw_history)
    assert coverage['cash_outcome_fills'].sum() == len(history)
    baseline = history[
        (history['timestamp_utc'] >= pd.Timestamp(manifest['effective_baseline_start_inclusive_utc'])) &
        (history['timestamp_utc'] < pd.Timestamp(manifest['main_baseline_end_exclusive_utc']))
    ]
    expected_baseline_counts = baseline.groupby('wallet').size().reindex(coverage.index, fill_value=0)
    np.testing.assert_array_equal(coverage['baseline_fills'], expected_baseline_counts)
    assert coverage.loc[coverage['baseline_fills'] == 0, 'history_status'].eq('no_baseline_fills_in_interval').all()
    token_mapping = pd.read_csv(data_path('history_token_mapping.csv'), dtype=str).set_index('token_id')
    assert token_mapping.index.is_unique
    expected_conditions = history['token_id'].map(token_mapping['condition_id'])
    assert expected_conditions.fillna('').eq(history['condition_id'].fillna('')).all()
    source_coverage = pd.read_csv(data_path('history_source_coverage.csv'))
    baseline_calendar_days = pd.date_range(
        pd.Timestamp(manifest['effective_baseline_start_inclusive_utc']).floor('D'),
        pd.Timestamp(manifest['main_baseline_end_exclusive_utc']).floor('D'), freq='D'
    ).strftime('%Y-%m-%d')
    assert source_coverage.set_index('day').loc[baseline_calendar_days, 'fills'].gt(0).all()

    report = {
        'status': 'passed', 'raw_fills': len(raw_history), 'normalized_fills': len(history),
        'scoped_fills_matched': len(scoped), 'wallets_checked': len(coverage),
        'checks': ['saved response and SQL hashes; no partial responses',
                   'all raw page values match history CSV exactly, without duplicate IDs',
                   'cash/outcome direction, integer amount scaling, and price identity',
                   'bounded UTC interval and main-cutoff overlap with scoped trades',
                   'baseline counts and explicit no-observed-history status',
                   'token-to-condition mapping and source rows on all baseline dates'],
    }
    save_metadata('history_verification', report)
    print(json.dumps(report, indent=2))



# Verify metrics

def synthetic_checks(config):
    cutoff = pd.Timestamp(config['analysis_cutoff'])
    baseline_start = pd.Timestamp(config['candidate_history']['effective_baseline_start_inclusive_utc'])
    target = config['markets'][0]
    rows = []
    for day in range(3):
        for condition in ['other_a', 'other_b']:
            for side in ['BUY', 'SELL']:
                rows.append(dict(wallet='established', token_id='other_token', side=side,
                                 cash=100.0, shares=200.0, condition_id=condition,
                                 timestamp_utc=baseline_start + pd.Timedelta(days=day, hours=1)))
            rows.append(dict(wallet='buy_only_history', token_id='other_token', side='BUY',
                             cash=100.0, shares=200.0, condition_id=condition,
                             timestamp_utc=baseline_start + pd.Timedelta(days=day, hours=1)))
    for side, token, count in [('BUY', target['yes_token'], 4), ('SELL', target['no_token'], 2)]:
        for trade_number in range(count):
            rows.append(dict(wallet='established', token_id=token, side=side, cash=150.0,
                             shares=300.0, condition_id=target['condition_id'],
                             timestamp_utc=cutoff - pd.Timedelta(hours=1)))
    rows.append(dict(wallet='no_history', token_id=target['yes_token'], side='BUY',
                     cash=100.0, shares=200.0, condition_id=target['condition_id'],
                     timestamp_utc=cutoff - pd.Timedelta(minutes=30)))
    rows.append(dict(wallet='buy_only_history', token_id=target['no_token'], side='SELL',
                     cash=100.0, shares=200.0, condition_id=target['condition_id'],
                     timestamp_utc=cutoff - pd.Timedelta(minutes=30)))
    for index, row in enumerate(rows):
        row['id'] = f'0x{index:064x}_0'
    history = pd.DataFrame(rows)
    scoped = history[history['condition_id'] == target['condition_id']].copy()
    scoped['market'] = target['key']
    scoped['outcome'] = np.where(scoped['token_id'] == target['yes_token'], 'Yes', 'No')
    wallets = ['established', 'no_history', 'buy_only_history']
    metrics = calculate_metrics(history, scoped, wallets, config).set_index('wallet')
    expected = metrics.loc['established']
    np.testing.assert_allclose(expected['metric_timing'], 71 / 72)
    np.testing.assert_allclose(expected['own_volume_ratio'], 5 / 3)
    np.testing.assert_allclose(expected['metric_volume'], 0.25)
    np.testing.assert_allclose(expected['activity_rate_ratio'], 2)
    np.testing.assert_allclose(expected['metric_activity'], 1 / 3)
    np.testing.assert_allclose(expected['baseline_market_hhi'], 0.5)
    assert expected['metric_concentration'] == 1 and expected['metric_direction'] == 1
    assert expected['metric_size'] == 1
    assert metrics.loc['no_history', ['metric_volume', 'metric_activity', 'metric_concentration']].isna().all()
    assert pd.isna(metrics.loc['buy_only_history', 'metric_volume'])

    # Splitting executions within the same transaction must not manufacture
    # larger volume, more activity, stronger timing, or greater concentration.
    split_first = history.copy()
    split_second = history.copy()
    for frame, suffix in [(split_first, '_first'), (split_second, '_second')]:
        frame['cash'] /= 2
        frame['shares'] /= 2
        frame['id'] += suffix
    split_history = pd.concat([split_first, split_second], ignore_index=True)
    split_scoped = pd.concat([scoped.assign(cash=scoped['cash'] / 2, shares=scoped['shares'] / 2, id=scoped['id'] + '_first'),
                              scoped.assign(cash=scoped['cash'] / 2, shares=scoped['shares'] / 2, id=scoped['id'] + '_second')], ignore_index=True)
    split_metrics = calculate_metrics(split_history, split_scoped, wallets, config).set_index('wallet')
    pd.testing.assert_frame_equal(metrics[METRIC_COLUMNS], split_metrics[METRIC_COLUMNS])

    # A complete reversal is removed from directional flow, even when gross
    # favorable turnover remains large enough to pass the broad screen.
    reversed_scoped = scoped.copy()
    favorable = reversed_scoped[reversed_scoped['wallet'] == 'established'].copy()
    favorable['side'] = favorable['side'].map({'BUY': 'SELL', 'SELL': 'BUY'})
    favorable['id'] += '_reverse'
    reversed_scoped = pd.concat([reversed_scoped, favorable], ignore_index=True)
    reversed_metrics = calculate_metrics(history, reversed_scoped, wallets, config).set_index('wallet')
    assert reversed_metrics.loc['established', 'metric_direction'] == 0
    earlier = calculate_metrics(history, scoped, wallets, config, cutoff=cutoff-pd.Timedelta(hours=2)).set_index('wallet')
    assert earlier['eligible_in_scenario'].eq(False).all()
    assert earlier['metric_timing'].isna().all()
    # A late-cutoff scenario must not add a partial first day to the median.
    partial_day = history.iloc[[0]].copy()
    partial_day['id'] = '0x' + 'f' * 64 + '_partial'
    partial_day['timestamp_utc'] = baseline_start + pd.Timedelta(minutes=30)
    partial_day['condition_id'] = 'partial_market'
    partial_day['cash'] = 1000000.0
    extended = pd.concat([history, partial_day], ignore_index=True)
    late = calculate_metrics(extended, scoped, wallets, config, cutoff=cutoff+pd.Timedelta(hours=1)).set_index('wallet')
    assert late.loc['established', 'baseline_buy_market_day_count'] == 6



def verify_metrics():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    synthetic_checks(config)
    wallets = pd.read_csv(data_path('candidates.csv'))['wallet'].tolist()
    columns = ['id', 'wallet', 'token_id', 'side', 'cash', 'shares', 'timestamp_utc', 'condition_id']
    history = pd.read_csv(data_path('history_trades.csv'), usecols=columns, dtype={'token_id': str})
    scoped = pd.read_csv(data_path('trades.csv'), dtype={'token_id': str})
    for frame in [history, scoped]:
        frame['timestamp_utc'] = pd.to_datetime(frame['timestamp_utc'], utc=True)
    metrics = calculate_metrics(history, scoped, wallets, config)
    saved_metrics = pd.read_csv(data_path('candidate_metrics.csv'))
    saved_metrics['last_directional_trade_utc'] = pd.to_datetime(saved_metrics['last_directional_trade_utc'], utc=True)
    pd.testing.assert_frame_equal(metrics, saved_metrics, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12)

    # Modifying all amounts after the main cutoff cannot affect any result,
    # including the percentile population and explanatory history statistics.
    cutoff = pd.Timestamp(config['analysis_cutoff'])
    changed_history = history.copy()
    changed_scoped = scoped.copy()
    for frame in [changed_history, changed_scoped]:
        frame.loc[frame['timestamp_utc'] >= cutoff, ['cash', 'shares']] = 999999999.0
    changed_metrics = calculate_metrics(changed_history, changed_scoped, wallets, config)
    pd.testing.assert_frame_equal(metrics, changed_metrics)
    assert len(metrics) == len(wallets) == 116
    assert metrics['wallet'].is_unique and metrics['eligible_in_scenario'].all()
    assert not {'score', 'rank'} & set(metrics.columns)
    no_history = metrics['baseline_fills'] == 0
    assert metrics.loc[no_history, ['metric_volume', 'metric_activity', 'metric_concentration']].isna().all().all()
    report = {
        'status': 'passed', 'wallets': len(metrics),
        'checks': ['hand-calculated timing, volume, activity, HHI and target-share fixtures',
                   'missing and unmatched-side history stays unavailable, not maximal',
                   'partial fills in one transaction do not change the six metric inputs',
                   'round-trip direction is zero and earlier-cutoff wallets remain in the cohort',
                   'saved metrics reproduce and post-cutoff amounts cannot change any column',
                   'no combined scores or ranks generated'],
    }
    save_metadata('metrics_verification', report)
    print(json.dumps(report, indent=2))



# Verify ranking

def verify_ranking():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    settings = config['ranking']
    metrics = pd.read_csv(data_path('candidate_metrics.csv'))
    ranking = pd.read_csv(data_path('ranking.csv'))
    reproduced = rank_candidates(metrics, settings)
    reproduced['missing_metrics'] = reproduced['missing_metrics'].replace('', np.nan)
    pd.testing.assert_frame_equal(reproduced, ranking, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12)
    for row in ranking.to_dict('records'):
        supported = math.fsum(row[column] * weight * 100 for column, weight in settings['weights'].items() if pd.notna(row[column]))
        available = math.fsum(weight for column, weight in settings['weights'].items() if pd.notna(row[column]))
        np.testing.assert_allclose(row['score'], supported / available, rtol=0, atol=1e-12)
        np.testing.assert_allclose(row['supported_score'], supported, rtol=0, atol=1e-12)
        np.testing.assert_allclose(row['coverage_percent'], available * 100, rtol=0, atol=1e-12)
        np.testing.assert_allclose(row['supported_score_upper_bound'], supported + (1-available)*100, atol=1e-12)
        for column, weight in settings['weights'].items():
            expected_weight = weight / available if pd.notna(row[column]) else 0
            np.testing.assert_allclose(row[column.replace('metric_', 'effective_weight_')], expected_weight, atol=1e-12)
            np.testing.assert_allclose(row[column.replace('metric_', 'contribution_')], row[column] * expected_weight * 100 if pd.notna(row[column]) else 0, atol=1e-12)
    contribution_columns = [column.replace('metric_', 'contribution_') for column in METRIC_COLUMNS]
    np.testing.assert_allclose(ranking[contribution_columns].sum(axis=1), ranking['score'], atol=1e-12)
    assert ranking['score'].between(0,100).all()
    assert set(ranking['wallet']) == set(metrics['wallet'])
    group_sets = []
    for group in ['complete', 'incomplete']:
        subset = ranking[ranking['ranking_group'].eq(group)].reset_index(drop=True)
        saved = pd.read_csv(data_path(f'ranking_{group}.csv'))
        pd.testing.assert_frame_equal(subset, saved, check_dtype=False, atol=1e-12)
        complete = saved[METRIC_COLUMNS].notna().all(axis=1)
        assert complete.eq(group == 'complete').all()
        assert saved['wallet'].tolist() == saved.sort_values(['score','wallet'], ascending=[False,True])['wallet'].tolist()
        np.testing.assert_array_equal(saved['rank'], saved['score'].rank(method='min', ascending=False))
        group_sets.append(set(saved['wallet']))
    assert not group_sets[0] & group_sets[1]
    assert group_sets[0] | group_sets[1] == set(metrics['wallet'])

    # Edge cases: partial coverage no longer caps the score; ranks restart in
    # each group; ties, zero weights and zero available evidence stay explicit.
    rows = []
    for wallet, value in [('complete_max',1.), ('complete_zero',0.), ('missing_max',1.), ('missing_half',.5), ('tie_a',.5), ('tie_b',.5)]:
        row = dict(wallet=wallet, eligible_in_scenario=True)
        row.update({column:value for column in METRIC_COLUMNS})
        if wallet.startswith('missing'):
            for column in ['metric_volume','metric_activity','metric_concentration']:
                row[column] = np.nan
        rows.append(row)
    rows.append(dict(rows[0], wallet='outside_gate', eligible_in_scenario=False))
    rows.append(dict(wallet='no_metrics',eligible_in_scenario=True,**{column:np.nan for column in METRIC_COLUMNS}))
    fixtures = pd.DataFrame(rows)
    checked = rank_candidates(fixtures, settings).set_index('wallet')
    assert checked.loc['complete_max','score'] == checked.loc['missing_max','score'] == 100
    assert checked.loc['complete_max','rank'] == checked.loc['missing_max','rank'] == 1
    assert checked.loc['missing_half','score'] == 50
    assert checked.loc['missing_half','supported_score'] == 25
    assert checked.loc['missing_max','coverage_percent'] == 50
    assert checked.loc['complete_zero','score'] == 0
    assert checked.loc['tie_a','rank'] == checked.loc['tie_b','rank']
    assert pd.isna(checked.loc['outside_gate','rank'])
    assert pd.isna(checked.loc['no_metrics','rank']) and pd.isna(checked.loc['no_metrics','score'])
    assert checked.loc['missing_max',['metric_volume','metric_activity','metric_concentration']].isna().all()
    shuffled = rank_candidates(fixtures.sample(frac=1,random_state=7),settings).set_index('wallet')
    pd.testing.assert_frame_equal(checked,shuffled)
    zero_settings = dict(settings, weights=dict.fromkeys(METRIC_COLUMNS,0.))
    zero_settings['weights']['metric_volume'] = 1.
    zero_result = rank_candidates(fixtures,zero_settings).set_index('wallet')
    assert pd.isna(zero_result.loc['missing_max','score']) and pd.isna(zero_result.loc['missing_max','rank'])
    summary = load_metadata('ranking_summary')
    assert summary['metrics_sha256'] == hashlib.sha256(data_path('candidate_metrics.csv').read_bytes()).hexdigest()
    output = {'status':'passed','ranked_wallets':len(ranking),
              'complete_wallets':len(group_sets[0]),'incomplete_wallets':len(group_sets[1]),
              'checks':['independent available-weight scores, effective weights and contributions',
                        'two disjoint rankings cover the whole selected cohort, ranks restart per group',
                        'complete scores unchanged; missing values preserved; 50 percent coverage can score 100',
                        'ties, ordering, outside-gate and zero-available-weight cases',
                        'saved tables reproduced and input metric hash verified']}
    save_metadata('ranking_verification',output)
    print(json.dumps(output,indent=2))


def verify_sensitivity():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    report = load_metadata('sensitivity_summary')
    parameters = load_metadata('sensitivity_parameters')
    summary = pd.read_csv(data_path('sensitivity_summary.csv')).set_index(['scenario','ranking_group'])
    details = pd.read_csv(data_path('sensitivity_rankings.csv'))
    main = pd.read_csv(data_path('ranking.csv')).set_index('wallet')
    wallets = set(main.index)
    scoped = pd.read_csv(data_path('trades.csv'),usecols=['wallet','timestamp_utc','market','outcome','side','cash','shares'])
    scoped['timestamp_utc'] = pd.to_datetime(scoped['timestamp_utc'],utc=True)
    definitions = scenario_definitions(config,config['timing_context'])
    assert len(definitions) == len(parameters) == report['scenario_count'] == 15
    assert len(summary) == report['group_summary_rows'] == 30
    assert set(summary.index) == {(d['name'],g) for d in definitions for g in ['complete','incomplete']}
    assert len(details) == 15*len(wallets)
    for parameter in parameters:
        name = parameter['name']
        rows = details[details['scenario'].eq(name)].set_index('wallet')
        assert set(rows.index) == wallets and rows.index.is_unique
        cutoff = pd.Timestamp(parameter['resolved_cutoff'])
        totals = screening_totals(scoped,config['data_preparation']['screening_market'],cutoff,parameter['resolved_window_hours'])
        full_pool = set(totals.loc[totals['directional_cash']>=parameter['resolved_threshold_usdc'],'wallet'])
        eligible_wallets = full_pool & wallets
        complete = rows[METRIC_COLUMNS].notna().all(axis=1)
        assert rows['ranking_group'].eq(np.where(complete,'complete','incomplete')).all()
        if name == 'complete_cases_only':
            eligible_wallets &= set(rows.index[complete])
        assert set(rows.index[rows['eligible_in_scenario']]) == eligible_wallets
        assert rows.loc[~rows['eligible_in_scenario'],'rank'].isna().all()
        weights = pd.Series(parameter['resolved_weights'])
        supported = rows[METRIC_COLUMNS].fillna(0).mul(weights).sum(axis=1)*100
        available = rows[METRIC_COLUMNS].notna().mul(weights).sum(axis=1)
        normalized = parameter['resolved_policy'] == 'split_cohorts_available_weight_normalization'
        expected = supported / available.replace(0,np.nan) if normalized else supported
        np.testing.assert_allclose(rows['supported_score'],supported,atol=1e-12)
        np.testing.assert_allclose(rows['coverage_percent'],available*100,atol=1e-12)
        np.testing.assert_allclose(rows['score'],expected,atol=1e-12)
        contributions = [col.replace('metric_','contribution_') for col in METRIC_COLUMNS]
        np.testing.assert_allclose(rows[contributions].sum(axis=1,min_count=1),expected,atol=1e-12)
        for group in ['complete','incomplete']:
            eligible = rows[rows['eligible_in_scenario'] & rows['ranking_group'].eq(group) & rows['score'].notna()]
            eligible = eligible.reset_index().sort_values(['score','wallet'],ascending=[False,True]).set_index('wallet')
            np.testing.assert_array_equal(eligible['rank'],eligible['score'].rank(method='min',ascending=False))
            record = summary.loc[(name,group)]
            assert record['ranked_wallets'] == len(eligible)
            assert record['full_screened_pool'] == len(full_pool)
            assert record['outside_collected_pool'] == len(full_pool-wallets)
            assert record['full_alternative_pool_scored'] == (set(rows.index[rows['eligible_in_scenario']]) == full_pool)
            main_group = main[main['ranking_group'].eq(group)].sort_values(['score','wallet'],ascending=[False,True])
            main_top = set(main_group.head(config['sensitivity']['top_count']).index)
            assert record['top10_overlap_with_main'] == len(set(eligible.head(config['sensitivity']['top_count']).index)&main_top)
            common = sorted(set(main_group.index)&set(eligible.index))
            assert record['same_group_common_wallets'] == len(common)
            correlation = main.loc[common,'score'].rank().corr(eligible.loc[common,'score'].rank()) if len(common)>2 else np.nan
            np.testing.assert_allclose(record['spearman_with_main_on_common_wallets'],correlation,atol=1e-12,equal_nan=True)
            if len(eligible):
                assert record['leader_wallet'] == eligible.index[0]
                np.testing.assert_allclose(record['leader_score'],eligible.iloc[0]['score'],atol=1e-12)
    reference = details[details['scenario'].eq('main')].set_index('wallet').sort_index()
    np.testing.assert_allclose(reference['score'],main.sort_index()['score'],atol=1e-12)
    np.testing.assert_array_equal(reference['rank'],main.sort_index()['rank'])
    np.testing.assert_array_equal(reference['ranking_group'],main.sort_index()['ranking_group'])
    stability = pd.read_csv(data_path('candidate_stability.csv')).set_index('wallet')
    eligible_details = details[details['eligible_in_scenario'] & details['rank'].notna()]
    for label, subset in [('all',eligible_details),('parameter',eligible_details[~eligible_details['family'].isin(['missing_policy','selection'])])]:
        for group in ['complete','incomplete']:
            grouped = subset[subset['ranking_group'].eq(group)]
            stats = grouped.groupby('wallet')['rank'].agg(['min','max','count']).reindex(stability.index)
            prefix = f'{label}_{group}'
            np.testing.assert_allclose(stability[f'{prefix}_best_rank_when_eligible'],stats['min'],equal_nan=True)
            np.testing.assert_allclose(stability[f'{prefix}_worst_rank_when_eligible'],stats['max'],equal_nan=True)
            np.testing.assert_array_equal(stability[f'{prefix}_eligible_scenarios'],stats['count'].fillna(0))
            top_counts = grouped[grouped['rank']<=10].groupby('wallet').size().reindex(stability.index).fillna(0)
            np.testing.assert_array_equal(stability[f'{prefix}_top10_appearances'],top_counts)
    for name,expected_hash in report['main_artifact_hashes'].items():
        assert hashlib.sha256(data_path(name).read_bytes()).hexdigest() == expected_hash
    output = {'status':'passed','scenarios':len(parameters),'group_summaries':len(summary),'rows_checked':len(details),
              'checks':['independent scenario scores, coverage and group-local ranks',
                        'screening gates and missing outside-pool history reconciled',
                        'group leaders, top overlap and same-group correlation reproduced',
                        'stability ranges and top counts verified separately by group',
                        'reference agrees with both main groups; protected hashes match']}
    save_metadata('sensitivity_verification',output)
    print(json.dumps(output,indent=2))



def run_checks():
    """Check all saved stages without regenerating their analytical results."""
    for check in [audit_coverage, verify_normalization, verify_history,
                  verify_metrics, verify_ranking, verify_sensitivity]:
        print(f'Running {check.__name__}', flush=True)
        check()


if __name__ == '__main__':
    run_checks()
