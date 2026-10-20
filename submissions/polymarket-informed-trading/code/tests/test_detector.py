import numpy as np
import pandas as pd
import pytest

import config
import detect_surprises as ds
from conftest import T0, market_row, price_path


# --- jump timing -----------------------------------------------------------------------

def test_late_sustained_jump_is_found():
    wp = np.array([0.07] * 200 + [0.95] * 30)
    assert ds.detect_jump(np.arange(len(wp)) * 600, wp) == 200


def test_isolated_spike_is_not_a_jump():
    wp = np.array([0.2] * 100 + [0.9] + [0.2] * 100 + [0.97] * 30)
    assert ds.detect_jump(np.arange(len(wp)) * 600, wp) == 201


def test_short_spike_run_is_not_a_jump():
    wp = np.array([0.2] * 100 + [0.85] * 5 + [0.2] * 100 + [0.97] * 30)
    assert ds.detect_jump(np.arange(len(wp)) * 600, wp) == 205


def test_no_jump_when_price_ends_low():
    wp = np.array([0.2] * 100 + [0.9] * 10 + [0.3] * 50)
    assert ds.detect_jump(np.arange(len(wp)) * 600, wp) is None


def test_summary_prices():
    wp = np.array([0.10] * 100 + [0.30] * 300 + [0.95] * 100)
    ts = np.arange(len(wp)) * 600
    s = ds.summarize_market(ts, wp, np.full(len(wp), 10.0))
    assert s["p_early"] == pytest.approx(0.10, abs=0.005)
    assert s["p_late"] == pytest.approx(0.95)
    assert s["jump_ts"] == ts[400]
    assert s["p_post"] == pytest.approx(0.95)


# --- event selection -------------------------------------------------------------------

def _surprise(cid, start_ts, n_pre=200, n_post=200, outcome_index=0, pre=0.07, post=0.96):
    """Cheap winner that jumps half-way through the tape and stays there."""
    p = pre if outcome_index == 0 else 1 - pre
    q = post if outcome_index == 0 else 1 - post
    a = price_path(cid, start_ts, [p] * n_pre, step=1800, outcome_index=outcome_index)
    jump_at = start_ts + n_pre * 1800
    b = price_path(cid, jump_at, [q] * n_post, step=1800, outcome_index=outcome_index)
    return a + b, jump_at


def test_detect_keeps_in_window_surprise(make_db):
    trades, jump_at = _surprise("c1", T0)
    con = make_db([market_row("c1", "surprise-market")], trades)
    row = ds.detect(con).set_index("slug").loc["surprise-market"]
    assert row["jump_ts"] == jump_at
    assert row["p_early"] == pytest.approx(0.07)
    assert not row["history_truncated"]


def test_detect_uses_winning_side_price(make_db):
    trades, jump_at = _surprise("c1", T0, outcome_index=1)
    con = make_db([market_row("c1", "m1")], trades)
    row = ds.detect(con).iloc[0]
    assert row["p_early"] == pytest.approx(0.07)
    assert row["jump_ts"] == jump_at


def test_detect_drops_jump_outside_window(make_db):
    before = int(pd.Timestamp("2025-09-01", tz="UTC").timestamp())
    t_old, _ = _surprise("old", before)
    t_new, _ = _surprise("new", T0)
    con = make_db([market_row("old", "will-trump-pardon-changpeng-zhao-in-2025"),
                   market_row("new", "in-window-market")], t_old + t_new)
    out = ds.detect(con)
    assert set(out["slug"]) == {"in-window-market"}
    start = pd.Timestamp(config.WINDOW_START).timestamp()
    end = pd.Timestamp(config.WINDOW_END).timestamp()
    assert out["jump_ts"].between(start, end).all()


def test_jump_time_ignores_early_spike(make_db):
    spike = price_path("c1", T0, [0.07] * 50 + [0.9] + [0.07] * 149, step=1800)
    jump_at = T0 + 200 * 1800
    tail = price_path("c1", jump_at, [0.96] * 200, step=1800)
    con = make_db([market_row("c1", "m1")], spike + tail)
    assert ds.detect(con).iloc[0]["jump_ts"] == jump_at


def test_detect_requires_cheap_early_price(make_db):
    trades, _ = _surprise("fav", T0, pre=0.70)
    con = make_db([market_row("fav", "favourite-wins")], trades)
    assert ds.detect(con).empty


def test_event_screen_misses_jump_in_last_hours(make_db):
    # Known blind spot, covered by screen_wallets.py: p_late averages the last 10% of the
    # tape, so a jump in its final hours does not reach MIN_LATE_PRICE.
    pre = price_path("late", T0, [0.07] * 300, step=1800)
    post = price_path("late", T0 + 300 * 1800, [0.96] * 40, step=60)
    con = make_db([market_row("late", "late-break")], pre + post)
    assert ds.detect(con).empty
    paths = ds.market_paths(con)
    assert paths.iloc[0]["jump_ts"] == T0 + 300 * 1800


def test_detect_flags_truncated_history(make_db, monkeypatch):
    monkeypatch.setattr(ds, "TRUNCATION_TRADES", 300)
    trades, _ = _surprise("c1", T0)
    con = make_db([market_row("c1", "big-market")], trades)
    assert bool(ds.detect(con).iloc[0]["history_truncated"])


def test_detect_respects_volume_and_trade_floors(make_db):
    t1, _ = _surprise("small", T0)
    t2, _ = _surprise("thin", T0, n_pre=40, n_post=40)
    con = make_db([market_row("small", "small-volume", volume=10_000),
                   market_row("thin", "thin-market")], t1 + t2)
    assert ds.detect(con).empty


def test_substantive_filter_drops_mechanical_markets():
    df = pd.DataFrame({"slug": ["will-trump-say-tariff-10-times", "maduro-out-by-january-31",
                                "elon-musk-of-tweets-nov-1-8"]})
    assert list(ds.substantive(df)["slug"]) == ["maduro-out-by-january-31"]
