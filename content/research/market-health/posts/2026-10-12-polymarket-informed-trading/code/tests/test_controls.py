import pandas as pd
import pytest

from conftest import T0, market_row, trade_row
from src import controls


@pytest.mark.parametrize("raw,stem", [
    ("strikes-on-312", "strikes-on"),
    ("strikes-on-843", "strikes-on"),
    ("strikes-on", "strikes-on"),
    ("maduro-out-in-2025", "maduro-out-in-2025"),
    ("will-trump-praise-allah-again-by-april-15-423", "will-trump-praise-allah-again-by"),
    ("us-anti-cartel-ground-operation-in-mexico-by-january-31",
     "us-anti-cartel-ground-operation-in-mexico-by"),
    ("who-will-trump-talk-to-in-november", "who-will-trump-talk-to-in-november"),
    ("israel-strikes-iran-by-january-9-2026", "strike-on-iran"),
    ("israel-strikes-iran-by-january-31-2026-894-994-453", "strike-on-iran"),
    ("us-strikes-iran-by-february-12-2026-525", "strike-on-iran"),
    ("us-next-strikes-iran-on-312", "strike-on-iran"),
    ("will-trump-pardon-changpeng-zhao-in-2025-162-949-658", "will-trump-pardon-changpeng-zhao-in-2025"),
])
def test_series_stem(raw, stem):
    assert controls.series_stem(raw) == stem


def _series_db(make_db):
    """Six 'strike on <date>' markets split over two event slugs; only day 3 resolves Yes."""
    markets, trades = [], []
    for d in range(6):
        won = d == 3
        markets.append(market_row(f"d{d}", f"strike-on-day-{d}",
                                  event_slug="strikes-on-312" if d < 3 else "strikes-on-843",
                                  win_index=0 if won else 1, win_outcome="Yes" if won else "No"))
        # fan bettor buys cheap Yes on every date before the winning jump
        trades.append(trade_row(f"d{d}", T0 + d * 60, 0.04, wallet="0xfan", size=5000))
    # sniper buys only the winning date
    trades.append(trade_row("d3", T0 + 100, 0.05, wallet="0xsniper", size=5000))
    # late buyer of a sibling, after the target jump: must not count
    trades.append(trade_row("d4", T0 + 10 * 86400, 0.04, wallet="0xsniper", size=5000))
    return make_db(markets, trades)


def _episodes(wallets):
    return pd.DataFrame({"wallet": wallets, "condition_id": "d3", "slug": "strike-on-day-3",
                         "win_index": 0, "jump_ts": float(T0 + 86400)})


def test_fan_bettor_is_demoted(make_db):
    con = _series_db(make_db)
    out = controls.sibling_record(con, _episodes(["0xfan", "0xsniper"])).set_index("wallet")
    assert out.loc["0xfan", "series_bets"] == 6
    assert out.loc["0xfan", "series_wins"] == 1
    assert out.loc["0xfan", "sib_tag"] == "fan_bettor"
    assert out.loc["0xfan", "M_sibling"] < 1.0


def test_single_targeted_bet_is_not_demoted(make_db):
    con = _series_db(make_db)
    out = controls.sibling_record(con, _episodes(["0xsniper"])).set_index("wallet")
    assert out.loc["0xsniper", "series_bets"] == 1
    assert out.loc["0xsniper", "sib_tag"] == "targeted"
    assert out.loc["0xsniper", "M_sibling"] == 1.0


def test_ladder_with_one_event_per_date_is_one_series(make_db):
    markets, trades = [], []
    for d in range(1, 5):
        won = d == 4
        markets.append(market_row(f"j{d}", f"x-strikes-y-by-january-{d}-2026",
                                  win_index=0 if won else 1, win_outcome="Yes" if won else "No"))
        trades.append(trade_row(f"j{d}", T0 + d * 60, 0.05, wallet="0xfan", size=5000))
    con = make_db(markets, trades)
    ep = pd.DataFrame({"wallet": ["0xfan"], "condition_id": ["j4"],
                       "slug": ["x-strikes-y-by-january-4-2026"], "win_index": [0],
                       "jump_ts": [float(T0 + 86400)]})
    out = controls.sibling_record(con, ep).iloc[0]
    assert (out["series_bets"], out["series_wins"]) == (4, 1)
    assert out["sib_tag"] == "fan_bettor"


def test_market_without_series_is_standalone(make_db):
    con = make_db([market_row("solo", "solo-market")],
                  [trade_row("solo", T0, 0.1, wallet="0xw", size=5000)])
    ep = pd.DataFrame({"wallet": ["0xw"], "condition_id": ["solo"], "slug": ["solo-market"],
                       "win_index": [0], "jump_ts": [float(T0 + 3600)]})
    out = controls.sibling_record(con, ep).iloc[0]
    assert out["sib_tag"] == "standalone"
    assert out["M_sibling"] == 1.0


@pytest.mark.parametrize("bets,wins,tag", [
    (1, 1, "targeted"), (2, 1, "targeted"), (3, 1, "fan_bettor"), (21, 1, "fan_bettor"),
    (4, 3, "targeted"), (6, 2, "fan_bettor"),
])
def test_sibling_multiplier(bets, wins, tag):
    m, t = controls.sibling_multiplier(bets, wins, has_series=True)
    assert t == tag
    assert (m < 1.0) == (tag == "fan_bettor")


@pytest.mark.parametrize("event_type,private_lead,tier", [
    ("election", False, "LOW"),
    ("legislative_vote", False, "LOW"),
    ("public_process", False, "LOW-MED"),
    ("public_process", True, "MED"),
    ("battlefield", False, "MED"),
    ("covert_military", False, "HIGH"),
    ("private_communication", True, "HIGH"),
])
def test_event_tier_rule(event_type, private_lead, tier):
    assert controls.event_tier(event_type, private_lead) == tier


def test_tier_multiplier_is_monotonic():
    m = [controls.TIER_MULT[t] for t in controls.TIERS]
    assert m == sorted(m, reverse=True)
    assert controls.TIER_MULT["HIGH"] == 1.0


def test_event_analysis_rejects_unknown_type(tmp_path):
    p = tmp_path / "ev.csv"
    pd.DataFrame({"slug": ["a"], "event": ["x"], "event_type": ["rumour"],
                  "private_lead": [False], "event_public_utc": ["2026-01-01 00:00"],
                  "source": ["s"], "note": [""]}).to_csv(p, index=False)
    with pytest.raises(ValueError):
        controls.load_event_analysis(p)


def test_event_analysis_adds_tier_and_multiplier(tmp_path):
    p = tmp_path / "ev.csv"
    pd.DataFrame({"slug": ["a", "b"], "event": ["x", "y"],
                  "event_type": ["covert_military", "election"], "private_lead": [False, False],
                  "event_public_utc": ["2026-01-03 09:22", "2026-02-01 00:00"],
                  "source": ["s", "s"], "note": ["", ""]}).to_csv(p, index=False)
    ev = controls.load_event_analysis(p).set_index("slug")
    assert ev.loc["a", "tier"] == "HIGH" and ev.loc["a", "M_event"] == 1.0
    assert ev.loc["b", "tier"] == "LOW" and ev.loc["b", "M_event"] < 0.5
