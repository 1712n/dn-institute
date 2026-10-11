"""Run the offline study or a selected stage; source collection is explicitly optional.

Each stage uses config.json and saved project data. Verification results and
stage summaries are consolidated in data/prepared/run_log.json.
"""

import argparse
from datetime import datetime, timezone

from collect import collect, collect_history
from prepare import prepare_trades, screen_candidates, save_metadata
from metrics import build_metrics
from ranking import build_ranking, check_sensitivity
from verify import (audit_coverage, verify_normalization, verify_history,
                    verify_metrics, verify_ranking, verify_sensitivity)


def run(stage='all', collect_source=False):
    """Execute stages in dependency order and stop immediately if a check fails."""
    if collect_source:
        collect()
    stages = {
        'prepare': [audit_coverage, prepare_trades, verify_normalization, screen_candidates],
        'history': [verify_history],
        'metrics': [build_metrics, verify_metrics],
        'ranking': [build_ranking, verify_ranking],
        'sensitivity': [check_sensitivity, verify_sensitivity],
    }
    if stage == 'collect-history':
        collect_history()
        return
    completed = []
    for name, actions in stages.items():
        if stage not in ('all', name):
            continue
        for action in actions:
            print(f'Running {action.__name__}', flush=True)
            action()
        completed.append(name)
    save_metadata('last_run', {'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                              'stages': completed, 'status': 'passed'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', default='all', choices=['all', 'prepare', 'history', 'metrics', 'ranking', 'sensitivity', 'collect-history'])
    parser.add_argument('--collect', action='store_true', help='Collect core-market source data before running the selected stages.')
    arguments = parser.parse_args()
    run(arguments.stage, arguments.collect)
