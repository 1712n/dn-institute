"""Calculate six candidate metrics and explanatory history statistics from prepared
trades. Save candidate_metrics.csv without changing screening or ranking rules.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from prepare import data_path, load_metadata, save_metadata, screening_totals

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT


# Calculate metrics

METRIC_COLUMNS = ['metric_timing', 'metric_size', 'metric_direction',
                  'metric_volume', 'metric_activity', 'metric_concentration']



def calculate_metrics(history, scoped_trades, wallets, config, cutoff=None, window_hours=None):
    cutoff = pd.Timestamp(config['analysis_cutoff']) if cutoff is None else pd.Timestamp(cutoff)
    preparation = config['data_preparation']
    settings = config['metrics']
    window_hours = preparation['screening_window_hours'] if window_hours is None else window_hours
    recent_start = cutoff - pd.Timedelta(hours=window_hours)
    baseline_start = pd.Timestamp(config['candidate_history']['effective_baseline_start_inclusive_utc'])
    baseline_days = (recent_start - baseline_start).total_seconds() / 86400
    recent_days = window_hours / 24
    assert baseline_days > 0
    assert history['id'].is_unique and scoped_trades['id'].is_unique
    assert history['condition_id'].notna().all(), 'History contains unmapped markets'
    market_key = preparation['screening_market']
    main_market = next(market for market in config['markets'] if market['key'] == market_key)

    all_wallet_totals = screening_totals(scoped_trades, market_key, cutoff, window_hours).set_index('wallet')
    results = all_wallet_totals.reindex(wallets).copy()
    # Earlier scenarios can precede a candidate's first target-market trade.
    # Retain that wallet with zero observed flows and no invented metric value.
    numeric_columns = all_wallet_totals.select_dtypes(include='number').columns
    results[numeric_columns] = results[numeric_columns].fillna(0)
    results['window_hours'] = window_hours
    results['window_start_inclusive_utc'] = recent_start.isoformat()
    results['cutoff_exclusive_utc'] = cutoff.isoformat()
    results['eligible_in_scenario'] = results['directional_cash'] >= preparation['selection_threshold_usdc']
    results['baseline_start_inclusive_utc'] = baseline_start.isoformat()
    results['baseline_end_exclusive_utc'] = recent_start.isoformat()
    results['baseline_days'] = baseline_days

    # Relative size uses all observed favorable-direction traders, not just
    # the selected pool. It is a contextual input, not an insider probability.
    positive_cash = all_wallet_totals.loc[all_wallet_totals['directional_cash'] > 0, 'directional_cash']
    size_percentiles = positive_cash.rank(method='average', pct=True)
    results['metric_size'] = size_percentiles.reindex(wallets).fillna(0)
    favorable_shares = results['yes_buy_shares'] + results['no_sell_shares']
    adverse_shares = results['yes_sell_shares'] + results['no_buy_shares']
    results['favorable_shares'] = favorable_shares
    results['adverse_shares'] = adverse_shares
    # A complete reversal or balanced YES/NO hedge has no net directional input.
    # This is trading flow, not reconstructed holdings or short-sale exposure.
    results['metric_direction'] = ((favorable_shares - adverse_shares) /
                                  (favorable_shares + adverse_shares).replace(0, np.nan)).clip(0, 1)

    history = history[history['wallet'].isin(wallets) & (history['timestamp_utc'] < cutoff)].copy()
    baseline = history[(history['timestamp_utc'] >= baseline_start) & (history['timestamp_utc'] < recent_start)].copy()
    recent = history[history['timestamp_utc'] >= recent_start].copy()
    for frame in [baseline, recent]:
        frame['day_bin'] = ((frame['timestamp_utc'] - baseline_start).dt.total_seconds() // 86400).astype('int64')
        frame['tx_hash'] = frame['id'].str.split('_').str[0]

    favorable_trades = recent[
        ((recent['token_id'] == main_market['yes_token']) & (recent['side'] == 'BUY')) |
        ((recent['token_id'] == main_market['no_token']) & (recent['side'] == 'SELL'))
    ].copy()
    # Cash-weighted proximity replaces a hard six-hour scoring cliff. The
    # six-hour share remains available as an interpretable diagnostic.
    favorable_trades['weighted_proximity'] = favorable_trades['cash'] * (
        1 - (cutoff - favorable_trades['timestamp_utc']).dt.total_seconds() / (window_hours * 3600)
    )
    weighted_proximity = favorable_trades.groupby('wallet')['weighted_proximity'].sum().reindex(wallets, fill_value=0)
    results['metric_timing'] = weighted_proximity / results['directional_cash'].replace(0, np.nan)
    late_start = cutoff - pd.Timedelta(hours=min(settings['late_window_hours'], window_hours))
    results['late_directional_cash'] = favorable_trades[favorable_trades['timestamp_utc'] >= late_start].groupby('wallet')['cash'].sum().reindex(wallets, fill_value=0)
    results['late_directional_cash_share'] = results['late_directional_cash'] / results['directional_cash'].replace(0, np.nan)
    results['last_directional_trade_utc'] = favorable_trades.groupby('wallet')['timestamp_utc'].max().reindex(wallets)

    baseline_active_days = baseline.groupby('wallet')['day_bin'].nunique().reindex(wallets, fill_value=0)
    results['baseline_active_days'] = baseline_active_days
    results['baseline_fills'] = baseline.groupby('wallet').size().reindex(wallets, fill_value=0)
    results['recent_all_market_fills'] = recent.groupby('wallet').size().reindex(wallets, fill_value=0)

    # Aggregate partial fills before taking medians: one observation is a
    # wallet/market/24-hour bin on one side, not one execution or outcome token.
    # Use only complete 24-hour intervals ending at the scenario's window
    # start. A shifted cutoff must not create a one-hour median observation.
    complete_days = int(np.floor(baseline_days))
    volume_baseline_start = recent_start - pd.Timedelta(days=complete_days)
    volume_baseline = baseline[baseline['timestamp_utc'] >= volume_baseline_start].copy()
    volume_baseline['day_bin'] = ((volume_baseline['timestamp_utc'] - volume_baseline_start).dt.total_seconds() // 86400).astype('int64')
    market_days = volume_baseline.groupby(['wallet', 'condition_id', 'day_bin', 'side'])['cash'].sum().reset_index()
    weighted_volume_ratios = pd.Series(0.0, index=results.index)
    volume_ready = pd.Series(True, index=results.index)
    for side, prefix, current_column in [('BUY', 'buy', 'yes_buy_cash'), ('SELL', 'sell', 'no_sell_cash')]:
        side_days = market_days[(market_days['side'] == side) & (market_days['cash'] > 0)]
        statistics = side_days.groupby('wallet')['cash'].agg(['median', 'count'])
        results[f'baseline_{prefix}_market_day_median'] = statistics['median'].reindex(wallets)
        results[f'baseline_{prefix}_market_day_count'] = statistics['count'].reindex(wallets, fill_value=0)
        results[f'baseline_{prefix}_active_days'] = side_days.groupby('wallet')['day_bin'].nunique().reindex(wallets, fill_value=0)
        results[f'recent_{prefix}_directional_cash_per_day'] = results[current_column] / recent_days
        has_current_flow = results[current_column] > 0
        side_ready = (
            (results[f'baseline_{prefix}_active_days'] >= settings['minimum_baseline_active_days']) &
            (results[f'baseline_{prefix}_market_day_count'] >= settings['minimum_market_day_observations_per_side'])
        )
        ratio = results[f'recent_{prefix}_directional_cash_per_day'] / results[f'baseline_{prefix}_market_day_median']
        results[f'{prefix}_volume_ratio'] = ratio.where(has_current_flow & side_ready)
        weighted_volume_ratios += (ratio * results[current_column]).fillna(0)
        volume_ready &= ~has_current_flow | side_ready
    volume_ready &= results['directional_cash'] > 0
    results['own_volume_ratio'] = (weighted_volume_ratios / results['directional_cash'].replace(0, np.nan)).where(volume_ready)
    # Only increases contribute: 1x -> 0, 2x -> 1/3, 10x -> 9/11.
    results['metric_volume'] = ((results['own_volume_ratio'] - 1) / (results['own_volume_ratio'] + 1)).clip(0, 1)
    results['volume_status'] = np.where(volume_ready, 'ready', 'insufficient_matching_side_history')

    # Transactions reduce sensitivity to one order being split into many fills.
    results['baseline_transactions'] = baseline.groupby('wallet')['tx_hash'].nunique().reindex(wallets, fill_value=0)
    results['recent_transactions'] = recent.groupby('wallet')['tx_hash'].nunique().reindex(wallets, fill_value=0)
    results['baseline_transactions_per_day'] = results['baseline_transactions'] / baseline_days
    results['recent_transactions_per_day'] = results['recent_transactions'] / recent_days
    activity_ready = (baseline_active_days >= settings['minimum_baseline_active_days']) & (results['baseline_transactions'] >= settings['minimum_baseline_transactions'])
    results['activity_rate_ratio'] = (results['recent_transactions_per_day'] / results['baseline_transactions_per_day'].replace(0, np.nan)).where(activity_ready)
    results['metric_activity'] = ((results['activity_rate_ratio'] - 1) / (results['activity_rate_ratio'] + 1)).clip(0, 1)
    results['activity_status'] = np.where(activity_ready, 'ready', 'insufficient_baseline_activity')

    # Turnover shares and HHI use both BUY and SELL to cover NO-only sellers.
    # HHI is diagnostic; only the shift toward the actual target market is a
    # ranking input, avoiding a second score for the same concentration change.
    for label, frame in [('baseline', baseline), ('recent', recent)]:
        market_cash = frame.groupby(['wallet', 'condition_id'])['cash'].sum().reset_index()
        all_cash = frame.groupby('wallet')['cash'].sum().reindex(wallets, fill_value=0)
        target_cash = frame[frame['condition_id'] == main_market['condition_id']].groupby('wallet')['cash'].sum().reindex(wallets, fill_value=0)
        results[f'{label}_all_market_cash'] = all_cash
        results[f'{label}_target_market_cash_share'] = target_cash / all_cash.replace(0, np.nan)
        market_cash['cash_share_squared'] = (market_cash['cash'] / market_cash['wallet'].map(all_cash)) ** 2
        results[f'{label}_market_hhi'] = market_cash.groupby('wallet')['cash_share_squared'].sum().reindex(wallets)
        results[f'{label}_market_count'] = frame.groupby('wallet')['condition_id'].nunique().reindex(wallets, fill_value=0)
    concentration_ready = (
        (baseline_active_days >= settings['minimum_baseline_active_days']) &
        (results['baseline_transactions'] >= settings['minimum_baseline_transactions_for_concentration']) &
        (results['baseline_all_market_cash'] > 0) & (results['recent_all_market_cash'] > 0)
    )
    results['target_market_share_change'] = results['recent_target_market_cash_share'] - results['baseline_target_market_cash_share']
    results['market_hhi_change'] = results['recent_market_hhi'] - results['baseline_market_hhi']
    results['metric_concentration'] = results['target_market_share_change'].clip(0, 1).where(concentration_ready)
    results['concentration_status'] = np.where(concentration_ready, 'ready', 'insufficient_baseline_turnover')
    results['history_status'] = np.where(results['baseline_fills'] > 0, 'baseline_observed', 'no_baseline_fills_in_interval')
    results['available_metric_count'] = results[METRIC_COLUMNS].notna().sum(axis=1)
    assert not np.isinf(results.select_dtypes(include='number').to_numpy(dtype=float)).any()
    for column in METRIC_COLUMNS:
        assert results[column].dropna().between(-1e-12, 1 + 1e-12).all(), column
    return results.reset_index().sort_values('wallet').reset_index(drop=True)



def build_metrics():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    wallets = pd.read_csv(data_path('candidates.csv'))['wallet'].tolist()
    columns = ['id', 'wallet', 'token_id', 'side', 'cash', 'shares', 'timestamp_utc', 'condition_id']
    history = pd.read_csv(data_path('history_trades.csv'), usecols=columns, dtype={'token_id': str})
    scoped = pd.read_csv(data_path('trades.csv'), dtype={'token_id': str})
    for frame in [history, scoped]:
        frame['timestamp_utc'] = pd.to_datetime(frame['timestamp_utc'], utc=True)
    metrics = calculate_metrics(history, scoped, wallets, config)
    metrics.to_csv(data_path('candidate_metrics.csv'), index=False)
    summary = {
        'status': 'calculated_not_ranked', 'wallets': len(metrics),
        'baseline_days': float(metrics['baseline_days'].iloc[0]),
        'ready_counts': {column: int(metrics[column].notna().sum()) for column in METRIC_COLUMNS},
        'positive_counts': {column: int(metrics[column].gt(0).sum()) for column in METRIC_COLUMNS},
        'wallets_without_baseline': int(metrics['baseline_fills'].eq(0).sum()),
        'wallets_with_all_metrics': int(metrics['available_metric_count'].eq(len(METRIC_COLUMNS)).sum()),
        'weights_applied': False,
    }
    save_metadata('metrics_summary', summary)
    print(json.dumps(summary, indent=2))

