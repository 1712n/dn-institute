import numpy as np
import pandas as pd
import pytest

import run_account_phase as rap

DAY = 86400.0
T_BET = 1_767_140_415.0


def _ep(age_days, vwap=0.07, notional=32538.0):
    first_act = T_BET - age_days * DAY if age_days is not None else np.nan
    return pd.DataFrame({"first_ts": [T_BET], "first_activity_ts": [first_act],
                         "vwap_entry": [vwap], "win_buy_notional": [notional]})


@pytest.mark.parametrize("age,vwap,notional,fresh", [
    (3.8, 0.07, 32538.0, True),     # created four days before its first bet
    (0.0, 0.22, 1000.0, True),      # first activity is the bet itself
    (7.0, 0.25, 1000.0, True),
    (7.1, 0.07, 32538.0, False),    # older than a week at the bet
    (3.8, 0.30, 32538.0, False),    # not a long shot
    (3.8, 0.07, 999.0, False),      # too small to matter
    (None, 0.07, 32538.0, False),   # no activity record
])
def test_fresh_bet_rule(age, vwap, notional, fresh):
    ep = rap.attach_wallet_age(_ep(age, vwap, notional))
    assert bool(ep["fresh_bet"].iloc[0]) is fresh


def test_wallet_age_is_measured_at_the_first_bet():
    ep = rap.attach_wallet_age(_ep(3.8))
    assert ep["wallet_age_days"].iloc[0] == pytest.approx(3.8)


def test_fresh_bet_counts_as_maximally_out_of_size():
    ep = rap.attach_wallet_age(_ep(3.8)).assign(v_ratio=1.2, a_ratio=1.9)
    ep = rap.cap_fresh_size(ep)
    assert np.isinf(ep["v_ratio"].iloc[0]) and np.isinf(ep["a_ratio"].iloc[0])
