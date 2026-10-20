import pandas as pd

import run_account_phase as rap
from src import episode_score as es


def _timed():
    return pd.DataFrame({"wallet": ["early", "reactor"],
                         "hours_before_jump": [6.4, 0.05], "hours_before_public": [2.9, -2.5],
                         "post_public_share": [0.0, 1.0]})


def test_news_reaction_is_demoted_and_loses_timing_points():
    ep = rap.public_timing(_timed()).set_index("wallet")
    assert ep.loc["reactor", "M_public"] < 1.0
    assert es.t_score(ep.loc["reactor", "t_hours"]) == 0


def test_entry_before_first_signal_keeps_full_weight():
    ep = rap.public_timing(_timed()).set_index("wallet")
    assert ep.loc["early", "M_public"] == 1.0
    assert es.t_score(ep.loc["early", "t_hours"]) == 2


def test_mostly_pre_public_episode_is_not_demoted():
    ep = pd.DataFrame({"wallet": ["w"], "hours_before_jump": [3.0], "hours_before_public": [1.0],
                       "post_public_share": [0.4]})
    assert rap.public_timing(ep).iloc[0]["M_public"] == 1.0


def test_public_time_is_the_earlier_of_signal_and_jump(tmp_path):
    p = tmp_path / "ev.csv"
    pd.DataFrame({"slug": ["a", "b", "c"],
                  "first_public_utc": ["2026-01-03 05:50", None, "2026-01-05 00:00"]}).to_csv(p, index=False)
    jump = pd.Timestamp("2026-01-03 09:22", tz="UTC").timestamp()
    tg = pd.DataFrame({"slug": ["a", "b", "c"], "jump_ts": [jump] * 3})
    out = rap.attach_public_time(tg, p).set_index("slug")["public_ts"]
    assert out["a"] == pd.Timestamp("2026-01-03 05:50", tz="UTC").timestamp()
    assert out["b"] == jump
    assert out["c"] == jump
