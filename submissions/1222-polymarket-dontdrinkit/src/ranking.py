"""Build separate complete/incomplete rankings and fifteen sensitivity scenarios. Save
reader-facing result tables and detailed supporting inputs in data/prepared/.
"""

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import copy
from prepare import data_path, load_metadata, save_metadata, screening_totals
from metrics import calculate_metrics, METRIC_COLUMNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT


# Rank candidates

def rank_candidates(metrics, settings):
    weights = settings['weights']
    assert set(weights) == set(METRIC_COLUMNS)
    assert all(np.isfinite(weight) and weight >= 0 for weight in weights.values())
    assert np.isclose(sum(weights.values()), 1, rtol=0, atol=1e-12)
    policy = settings['missing_metric_policy']
    assert policy in ['split_cohorts_available_weight_normalization', 'no_contribution_no_weight_redistribution']
    assert settings['tie_break'] == 'score_desc_then_wallet_asc'
    assert metrics['wallet'].is_unique
    for column in METRIC_COLUMNS:
        assert metrics[column].dropna().between(0, 1).all(), column

    ranking = metrics.copy()
    # Keep missing metric values. Zero contribution means no supported
    # evidence from this metric, not a measured zero or evidence of innocence.
    ranking['score'] = 0.0
    ranking['available_weight'] = 0.0
    for column, weight in weights.items():
        contribution_column = column.replace('metric_', 'contribution_')
        ranking[contribution_column] = ranking[column].fillna(0) * weight * 100
        ranking['score'] += ranking[contribution_column]
        ranking['available_weight'] += ranking[column].notna() * weight
    ranking['available_weight'] = ranking['available_weight'].clip(0, 1)
    ranking['missing_weight'] = (1 - ranking['available_weight']).clip(0, 1)
    ranking['coverage_percent'] = ranking['available_weight'] * 100
    ranking['supported_score'] = ranking['score']
    ranking['supported_score_upper_bound'] = (ranking['score'] + 100 * ranking['missing_weight']).clip(upper=100)
    ranking['missing_metrics'] = ranking[METRIC_COLUMNS].apply(
        lambda row: ','.join(column for column in METRIC_COLUMNS if pd.isna(row[column])), axis=1
    )
    ranking['coverage_status'] = np.where(ranking['missing_metrics'].eq(''), 'complete', 'incomplete')
    ranking['ranking_group'] = ranking['coverage_status']
    if policy == 'split_cohorts_available_weight_normalization':
        denominator = ranking['available_weight'].replace(0, np.nan)
        ranking['score'] = (ranking['supported_score'] / denominator).clip(0, 100)
        for column, weight in weights.items():
            ranking[column.replace('metric_', 'effective_weight_')] = ranking[column].notna() * weight / denominator
            ranking[column.replace('metric_', 'contribution_')] /= denominator
    ranking['ranking_status'] = np.where(ranking['eligible_in_scenario'], 'selected_for_review', 'outside_scenario_gate')
    # Unrounded scores determine order. Equal scores share a rank; wallet order
    # only makes tied rows reproducible, without favoring cash size or history.
    eligible = ranking['eligible_in_scenario'] & ranking['score'].notna()
    ranking['rank'] = pd.Series(pd.NA, index=ranking.index, dtype='Int64')
    ranking.loc[eligible, 'rank'] = ranking.loc[eligible].groupby('ranking_group')['score'].rank(method='min', ascending=False).astype('Int64')
    ranking = ranking.sort_values(['ranking_group', 'eligible_in_scenario', 'score', 'wallet'], ascending=[True, False, False, True])
    return ranking.reset_index(drop=True)



def build_ranking():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    metrics_path = data_path('candidate_metrics.csv')
    metrics = pd.read_csv(metrics_path)
    candidates = pd.read_csv(data_path('candidates.csv'))
    assert set(metrics['wallet']) == set(candidates['wallet'])
    assert metrics['eligible_in_scenario'].all()
    assert metrics['cutoff_exclusive_utc'].eq(pd.Timestamp(config['analysis_cutoff']).isoformat()).all()
    assert metrics['window_hours'].eq(config['data_preparation']['screening_window_hours']).all()
    ranking = rank_candidates(metrics, config['ranking'])

    summary_columns = ['wallet', 'rank', 'score', 'coverage_percent', 'supported_score',
                       'coverage_status', 'history_status', 'missing_metrics']
    summary = {
        'status': 'ranked',
        'weights': config['ranking']['weights'],
        'missing_metric_policy': config['ranking']['missing_metric_policy'],
        'ranked_wallets': len(ranking),
        'complete_coverage_wallets': int(ranking['coverage_status'].eq('complete').sum()),
        'incomplete_coverage_wallets': int(ranking['coverage_status'].eq('incomplete').sum()),
        'metrics_sha256': hashlib.sha256(metrics_path.read_bytes()).hexdigest(),
        'top_by_group': {group: ranking.loc[ranking['ranking_group'].eq(group), summary_columns].head(5).to_dict('records') for group in ['complete', 'incomplete']},
        'benchmark': ranking.loc[ranking['wallet'] == config['benchmark_wallet'], summary_columns].to_dict('records'),
        'limitations': [
            'Priority score measures supported signals, not a probability or legal conclusion.',
            'Incomplete scores normalize each wallet over its available metric weights; metric sets can differ.',
            'Ranks are local to complete/incomplete groups; scores across groups are not directly comparable.',
            'Supported-score upper bound refers to the unnormalized six-metric sum, not the normalized score.',
        ],
    }
    ranking.to_csv(data_path('ranking.csv'), index=False)
    for group in ['complete', 'incomplete']:
        ranking.loc[ranking['ranking_group'].eq(group)].to_csv(data_path(f'ranking_{group}.csv'), index=False)
    save_metadata('ranking_summary', summary)
    print(json.dumps(summary, indent=2))



# Check sensitivity

def scenario_definitions(config, timing):
    definitions = [{'name': 'main', 'family': 'reference'}]
    for scenario in timing['timing']['sensitivity_scenarios']:
        if pd.Timestamp(scenario['cutoff']) != pd.Timestamp(config['analysis_cutoff']):
            definitions.append(dict(name=scenario['name'], family='cutoff', cutoff=scenario['cutoff']))
    for hours in config['sensitivity']['window_variants_hours']:
        definitions.append(dict(name=f'window_{hours}h', family='window', window_hours=hours))
    for name, weights in config['sensitivity']['weight_variants'].items():
        definitions.append(dict(name=name, family='weights', weights=weights))
    for name, requirements in config['sensitivity']['history_requirement_variants'].items():
        definitions.append(dict(name=name, family='history_requirements', requirements=requirements))
    for threshold in config['sensitivity']['selection_threshold_variants_usdc']:
        definitions.append(dict(name=f'threshold_{threshold}', family='selection', threshold=threshold))
    for policy in config['sensitivity']['missing_metric_diagnostics']:
        definitions.append(dict(name=policy, family='missing_policy', diagnostic_policy=policy))
    assert len({item['name'] for item in definitions}) == len(definitions)
    return definitions



def check_sensitivity():
    config = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8-sig'))
    timing = json.loads((PROJECT_ROOT / 'config.json').read_text(encoding='utf-8'))['timing_context']
    assert config['sensitivity']['cohort_scope'] == 'fixed_collected_pool'
    assert config['sensitivity']['design'] == 'one_change_at_a_time'
    main_ranking = pd.read_csv(data_path('ranking.csv'))
    main_metrics = pd.read_csv(data_path('candidate_metrics.csv'))
    wallets = pd.read_csv(data_path('candidates.csv'))['wallet'].tolist()
    columns = ['id','wallet','token_id','side','cash','shares','timestamp_utc','condition_id']
    history = pd.read_csv(data_path('history_trades.csv'), usecols=columns, dtype={'token_id':str})
    scoped = pd.read_csv(data_path('trades.csv'), dtype={'token_id':str})
    for frame in [history, scoped]:
        frame['timestamp_utc'] = pd.to_datetime(frame['timestamp_utc'], utc=True)
    protected = {name: hashlib.sha256((data_path(name)).read_bytes()).hexdigest()
                 for name in ['ranking.csv','ranking_complete.csv','ranking_incomplete.csv','candidate_metrics.csv','candidates.csv']}
    main_top = {group: set(rows.head(config['sensitivity']['top_count'])['wallet']) for group, rows in main_ranking.groupby('ranking_group')}
    main_scores = main_ranking.set_index('wallet')['score']
    history_end = pd.Timestamp(config['candidate_history']['end_exclusive_utc'])
    collection_start = pd.Timestamp(config['collection_start'], tz='UTC')
    summaries, parameter_rows, result_frames = [], [], []

    for definition in scenario_definitions(config, timing):
        scenario_config = copy.deepcopy(config)
        cutoff = pd.Timestamp(definition.get('cutoff', config['analysis_cutoff']))
        hours = definition.get('window_hours', config['data_preparation']['screening_window_hours'])
        threshold = definition.get('threshold', config['data_preparation']['selection_threshold_usdc'])
        scenario_config['data_preparation']['selection_threshold_usdc'] = threshold
        scenario_config['metrics'].update(definition.get('requirements', {}))
        settings = copy.deepcopy(config['ranking'])
        settings['weights'] = definition.get('weights', settings['weights'])
        assert cutoff <= history_end and cutoff-pd.Timedelta(hours=hours) >= collection_start

        # Only date/window/history changes require the expensive history scan.
        if definition['family'] in ['reference','cutoff','window','history_requirements']:
            metrics = calculate_metrics(history, scoped, wallets, scenario_config, cutoff=cutoff, window_hours=hours)
        else:
            metrics = main_metrics.copy()
            metrics['eligible_in_scenario'] = metrics['directional_cash'] >= threshold
        if definition['name'] == 'main':
            saved = main_metrics.copy()
            saved['last_directional_trade_utc'] = pd.to_datetime(saved['last_directional_trade_utc'], utc=True)
            pd.testing.assert_frame_equal(metrics, saved, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12)

        policy = definition.get('diagnostic_policy', config['ranking']['missing_metric_policy'])
        if policy == 'complete_cases_only':
            metrics['eligible_in_scenario'] &= metrics[METRIC_COLUMNS].notna().all(axis=1)
        settings['missing_metric_policy'] = (policy if policy != 'complete_cases_only'
                                             else config['ranking']['missing_metric_policy'])
        ranked = rank_candidates(metrics, settings)

        full_totals = screening_totals(scoped, config['data_preparation']['screening_market'], cutoff, hours)
        full_pool = set(full_totals.loc[full_totals['directional_cash'] >= threshold,'wallet'])
        eligible_ranking = ranked[ranked['eligible_in_scenario']]
        observed_pool = set(wallets) & full_pool
        for group in ['complete', 'incomplete']:
            group_rows = eligible_ranking[eligible_ranking['ranking_group'].eq(group)]
            common = group_rows.set_index('wallet')['score']
            same_group = set(main_ranking.loc[main_ranking['ranking_group'].eq(group), 'wallet']) & set(common.index)
            common_wallets = sorted(same_group)
            correlation = main_scores.reindex(common_wallets).rank().corr(common.reindex(common_wallets).rank()) if len(common_wallets)>2 else np.nan
            top = group_rows.head(config['sensitivity']['top_count'])
            summaries.append({
                'scenario':definition['name'], 'family':definition['family'], 'policy':policy,
                'ranking_group':group,
                'cutoff_utc':cutoff.isoformat(), 'window_hours':hours, 'threshold_usdc':threshold,
                'baseline_days':float(metrics['baseline_days'].iloc[0]),
                'volume_baseline_complete_days':int(np.floor(metrics['baseline_days'].iloc[0])),
                'full_screened_pool':len(full_pool), 'screened_wallets_with_collected_history':len(observed_pool),
                'outside_collected_pool':len(full_pool-set(wallets)),
                'ranked_wallets':len(group_rows),
                'full_alternative_pool_scored':len(full_pool-set(wallets))==0 and set(eligible_ranking['wallet'])==full_pool,
                'top10_overlap_with_main':len(set(top['wallet']) & main_top.get(group,set())),
                'same_group_common_wallets':len(common_wallets),
                'spearman_with_main_on_common_wallets':correlation,
                'leader_wallet':top.iloc[0]['wallet'] if len(top) else '',
                'leader_score':float(top.iloc[0]['score']) if len(top) else np.nan,
            })
        parameter_rows.append(dict(**definition, resolved_cutoff=cutoff.isoformat(), resolved_window_hours=hours,
                                   resolved_threshold_usdc=threshold, resolved_weights=settings['weights'], resolved_policy=settings['missing_metric_policy'],
                                   resolved_history_requirements=scenario_config['metrics']))
        contribution_columns = [column.replace('metric_', 'contribution_') for column in METRIC_COLUMNS]
        result = ranked[['wallet','rank','score','supported_score','coverage_percent','coverage_status',
                         'ranking_group','available_metric_count','eligible_in_scenario','missing_metrics','baseline_days',
                         'baseline_active_days'] + METRIC_COLUMNS + contribution_columns].copy()
        result['scenario'] = definition['name']
        result['family'] = definition['family']
        result['policy'] = policy
        result_frames.append(result)
        print(f"{definition['name']}: {len(eligible_ranking)} ranked, {len(full_pool-set(wallets))} outside history pool", flush=True)

    details = pd.concat(result_frames, ignore_index=True)
    summary = pd.DataFrame(summaries)
    stability = main_ranking[['wallet','rank','score','coverage_percent','ranking_group']].rename(columns={'rank':'main_rank','score':'main_score','ranking_group':'main_group'}).copy()
    eligible_details = details[details['eligible_in_scenario'] & details['rank'].notna()]
    for label, subset in [('all',eligible_details), ('parameter',eligible_details[~eligible_details['family'].isin(['missing_policy','selection'])])]:
        for group in ['complete', 'incomplete']:
            grouped = subset[subset['ranking_group'].eq(group)]
            statistics = grouped.groupby('wallet')['rank'].agg(['min','max','count'])
            prefix = f'{label}_{group}'
            stability[f'{prefix}_best_rank_when_eligible'] = stability['wallet'].map(statistics['min'])
            stability[f'{prefix}_worst_rank_when_eligible'] = stability['wallet'].map(statistics['max'])
            stability[f'{prefix}_eligible_scenarios'] = stability['wallet'].map(statistics['count']).fillna(0).astype(int)
            stability[f'{prefix}_top10_appearances'] = stability['wallet'].map(grouped[grouped['rank']<=10].groupby('wallet').size()).fillna(0).astype(int)
    report = {
        'status':'complete_report_pending', 'scenario_count':len(parameter_rows), 'group_summary_rows':len(summary), 'cohort_wallets':len(wallets),
        'design':'one_change_at_a_time',
        'parameter_scenario_count':sum(item['family'] not in ['missing_policy','selection'] for item in parameter_rows),
        'main_artifact_hashes':protected,
        'limitations':['Scenario ranks, leaders and top sets are separate for complete/incomplete groups.',
                       'Candidate groups can change when history requirements, cutoff or window change.',
                       'Correlations use wallets in the same group in both main and scenario results.',
                       'Alternative rankings cover the fixed collected cohort; missing outside-pool histories are counted explicitly.',
                       'Rank ranges are not confidence intervals; parameter stability does not prove insider trading.'],
    }
    summary.to_csv(data_path('sensitivity_summary.csv'), index=False)
    details.to_csv(data_path('sensitivity_rankings.csv'), index=False)
    stability.to_csv(data_path('candidate_stability.csv'), index=False)
    save_metadata('sensitivity_parameters', parameter_rows)
    save_metadata('sensitivity_summary', report)
    for name, expected_hash in protected.items():
        assert hashlib.sha256((data_path(name)).read_bytes()).hexdigest()==expected_hash
    print(json.dumps(report, indent=2))

