"""Normalize source fills into trades, screen candidate addresses, and provide shared
data-path and metadata helpers. Inputs are saved source tables and config.json.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT


def data_path(name):
    """Resolve a generated table to a public result or a prepared input."""
    result_names = {'ranking.csv': 'ranking.csv', 'sensitivity_summary.csv': 'sensitivity.csv',
                    'candidate_stability.csv': 'candidate_stability.csv',
                    'ranking_complete.csv': 'ranking_complete.csv', 'ranking_incomplete.csv': 'ranking_incomplete.csv'}
    if name in result_names:
        return PROJECT_ROOT / 'results' / result_names[name]
    path = PROJECT_ROOT / 'data' / 'prepared' / name
    if not path.exists() and name in {'history_fills.csv', 'history_trades.csv'}:
        from restore_csv import restore_table
        restore_table(PROJECT_ROOT, path)
    return path


def load_metadata(name):
    """Read a named provenance record or stage result from the consolidated JSON."""
    provenance_names = {'collection_manifest', 'snapshot_manifest', 'history_manifest'}
    path = PROJECT_ROOT / 'data' / 'provenance.json' if name in provenance_names else data_path('run_log.json')
    return json.loads(path.read_text(encoding='utf-8'))[name]


def save_metadata(name, value):
    """Update one record while retaining the other pipeline stages and source receipts."""
    provenance_names = {'collection_manifest', 'snapshot_manifest', 'history_manifest'}
    path = PROJECT_ROOT / 'data' / 'provenance.json' if name in provenance_names else data_path('run_log.json')
    content = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    content[name] = value
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding='utf-8')



# Normalize trades

def normalize_trades(raw_fills, markets):
    """Convert cash/outcome fills into trades from each maker's perspective."""
    trades = raw_fills.copy()
    assert trades['id'].is_unique

    market_by_token = {}
    outcome_by_token = {}
    for market in markets:
        for token_key, outcome in [('yes_token', 'Yes'), ('no_token', 'No')]:
            token_id = market[token_key]
            market_by_token[token_id] = market['key']
            outcome_by_token[token_id] = outcome

    # Asset 0 is collateral. A maker giving cash buys outcome shares;
    # a maker receiving cash sells them. Keep one row per execution ID.
    is_buy = trades['maker_asset_id'].eq('0')
    is_sell = trades['taker_asset_id'].eq('0')
    assert (is_buy ^ is_sell).all(), 'Unexpected non-cash or cash/cash fill'
    trades['wallet'] = trades['maker'].str.lower()
    trades['token_id'] = trades['taker_asset_id'].where(is_buy, trades['maker_asset_id'])
    trades['side'] = np.where(is_buy, 'BUY', 'SELL')

    # Both collateral and outcome shares use six decimal places.
    # Cash is gross traded value; the source fee is retained separately.
    trades['cash'] = pd.to_numeric(
        trades['maker_amount_raw'].where(is_buy, trades['taker_amount_raw'])
    ) / 1_000_000
    trades['shares'] = pd.to_numeric(
        trades['taker_amount_raw'].where(is_buy, trades['maker_amount_raw'])
    ) / 1_000_000
    trades['price'] = trades['cash'] / trades['shares']
    trades['fee'] = pd.to_numeric(trades['fee_raw']) / 1_000_000
    trades['market'] = trades['token_id'].map(market_by_token)
    trades['outcome'] = trades['token_id'].map(outcome_by_token)
    trades['timestamp_utc'] = pd.to_datetime(
        trades['timestamp_epoch'].astype('int64'), unit='s', utc=True
    )
    # Several executions can share a transaction; do not deduplicate by hash.
    trades['tx_hash'] = trades['id'].str.split('_').str[0]
    trades['tx_url'] = 'https://polygonscan.com/tx/' + trades['tx_hash']

    assert trades['market'].notna().all(), 'Unmapped outcome token'
    assert trades['price'].between(0, 1.00001).all()
    assert (trades['shares'] > 0).all()
    assert trades['wallet'].str.fullmatch(r'0x[0-9a-f]{40}').all()
    assert trades['tx_hash'].str.fullmatch(r'0x[0-9a-f]{64}').all()
    return trades



def prepare_trades():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    raw_fills = pd.read_csv(data_path('fills.csv'), dtype=str)
    trades = normalize_trades(raw_fills, config['markets'])
    trades.to_csv(data_path('trades.csv'), index=False)
    print(f'Normalized {len(trades)} executions')



# Screen candidates

def screening_totals(trades, market, cutoff, window_hours):
    """Summarize each observed maker using only trades before the cutoff."""
    market_trades = trades[(trades['market'] == market) & (trades['timestamp_utc'] < cutoff)]
    window_start = cutoff - pd.Timedelta(hours=window_hours)
    window_trades = market_trades[market_trades['timestamp_utc'] >= window_start]
    totals = market_trades.groupby('wallet').size().to_frame('observed_fills_before_cutoff')
    totals['window_fills'] = window_trades.groupby('wallet').size().reindex(totals.index, fill_value=0)

    for outcome, side, prefix in [
        ('Yes', 'BUY', 'yes_buy'), ('Yes', 'SELL', 'yes_sell'),
        ('No', 'BUY', 'no_buy'), ('No', 'SELL', 'no_sell'),
    ]:
        matching_trades = window_trades[
            (window_trades['outcome'] == outcome) & (window_trades['side'] == side)
        ]
        amounts = matching_trades.groupby('wallet')[['cash', 'shares']].sum()
        for amount in ['cash', 'shares']:
            totals[f'{prefix}_{amount}'] = amounts[amount].reindex(totals.index, fill_value=0)

    # Gross favorable-direction turnover is a broad collection gate, not net
    # holdings or evidence of information. It can include inventory unwinding.
    totals['directional_cash'] = totals['yes_buy_cash'] + totals['no_sell_cash']
    totals['net_yes_shares'] = totals['yes_buy_shares'] - totals['yes_sell_shares']
    totals['net_no_shares'] = totals['no_buy_shares'] - totals['no_sell_shares']
    totals['yes_direction_share_change'] = totals['net_yes_shares'] - totals['net_no_shares']
    totals['window_start_inclusive_utc'] = window_start.isoformat()
    totals['cutoff_exclusive_utc'] = cutoff.isoformat()
    totals['window_hours'] = window_hours
    return totals.reset_index().sort_values('wallet').reset_index(drop=True)



def screen_candidates():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    preparation = config['data_preparation']
    assert preparation['screening_cash_basis'] == 'yes_buy_cash_plus_no_sell_cash'
    assert preparation['require_positive_net_position'] is False
    timing_config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))['timing_context']
    cutoff = pd.Timestamp(config['analysis_cutoff'])
    assert cutoff == pd.Timestamp(timing_config['timing']['analysis_cutoff'])
    window_hours = preparation['screening_window_hours']
    threshold = preparation['selection_threshold_usdc']
    market = preparation['screening_market']
    trades = pd.read_csv(data_path('trades.csv'), dtype={'token_id': str})
    trades['timestamp_utc'] = pd.to_datetime(trades['timestamp_utc'], utc=True)

    totals = screening_totals(trades, market, cutoff, window_hours)
    totals['selected_for_history'] = totals['directional_cash'] >= threshold
    totals['selection_threshold_usdc'] = threshold
    totals['selection_reason'] = 'below_directional_cash_threshold'
    totals.loc[totals['selected_for_history'], 'selection_reason'] = 'yes_buy_plus_no_sell_cash_at_least_threshold'
    candidates = totals[totals['selected_for_history']].copy()
    candidate_wallets = set(candidates['wallet'])

    # Alternative pools are diagnostics only; they do not silently expand the
    # main history request or claim that full historical scores are available.
    sensitivity_rows = []
    for scenario in timing_config['timing']['sensitivity_scenarios']:
        scenario_cutoff = pd.Timestamp(scenario['cutoff'])
        for scenario_hours in preparation['coverage_review_windows_hours']:
            assert scenario_cutoff - pd.Timedelta(hours=scenario_hours) >= pd.Timestamp(config['collection_start'], tz='UTC')
            assert scenario_cutoff <= pd.Timestamp(config['collection_end'], tz='UTC')
            scenario_totals = screening_totals(trades, market, scenario_cutoff, scenario_hours)
            for scenario_threshold in preparation['screening_sensitivity_thresholds_usdc']:
                selected_wallets = set(scenario_totals.loc[
                    scenario_totals['directional_cash'] >= scenario_threshold, 'wallet'
                ])
                sensitivity_rows.append({
                    'scenario': scenario['name'], 'cutoff_exclusive_utc': scenario_cutoff.isoformat(),
                    'window_hours': scenario_hours, 'threshold_usdc': scenario_threshold,
                    'candidate_count': len(selected_wallets),
                    'overlap_with_main_pool': len(selected_wallets & candidate_wallets),
                    'outside_main_pool': len(selected_wallets - candidate_wallets),
                    'main_pool_missing_in_scenario': len(candidate_wallets - selected_wallets),
                })

    assert candidates['wallet'].is_unique
    assert candidates['directional_cash'].ge(threshold).all()
    assert len(totals) == trades.loc[
        (trades['market'] == market) & (trades['timestamp_utc'] < cutoff), 'wallet'
    ].nunique()

    report = {
        'stage': 'candidate_screening', 'status': 'complete', 'market': market,
        'cutoff_exclusive_utc': cutoff.isoformat(), 'window_hours': window_hours,
        'threshold_usdc': threshold, 'cash_basis': preparation['screening_cash_basis'],
        'requires_positive_net_position': False,
        'observed_wallets_before_cutoff': len(totals), 'selected_wallets': len(candidates),
        'wallets_with_yes_buys_at_least_threshold': int(candidates['yes_buy_cash'].ge(threshold).sum()),
        'additional_wallets_from_no_sells': int(candidates['yes_buy_cash'].lt(threshold).sum()),
        'selected_with_nonpositive_yes_direction_share_change': int(candidates['yes_direction_share_change'].le(0).sum()),
        'benchmark_selected_by_same_rule': config['benchmark_wallet'] in candidate_wallets,
        'sensitivity_scenarios': len(sensitivity_rows),
        'history_pool_scope': 'main_screening_only',
        'limitations': [
            'A candidate is a history-collection target, not an insider classification.',
            'NO sells can unwind inventory; gross turnover can include hedged or reversed trades.',
            'Window share changes do not reconstruct initial holdings.',
            'Sensitivity-only wallets have no detailed history collected at this stage.',
        ],
    }
    totals.to_csv(data_path('screening.csv'), index=False)
    candidates.to_csv(data_path('candidates.csv'), index=False)
    pd.DataFrame(sensitivity_rows).to_csv(data_path('screening_sensitivity.csv'), index=False)
    save_metadata('screening_summary', report)
    print(json.dumps(report, indent=2))

