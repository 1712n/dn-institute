"""End-to-end checks on the real dataset (skipped when the DuckDB file is absent)."""
import hashlib

import duckdb
import pandas as pd
import pytest

import config

MADURO = "maduro-out-by-january-31-2026-318"
MADURO_WALLET = "0x31a56e9e690c621ed21de08cb559e9524cdb8ed9"
CZ = "will-trump-pardon-changpeng-zhao-in-2025-162-949-658"
IRAN = "will-the-us-next-strike-iran-on-february-28-2026-et"
IRAN_FAN_BETTORS = {"Embarrassed-Wording", "Next-Reader", "Present-Plunger", "Automatic-Decade"}

OUTPUTS = {
    "surprise_markets.csv": {"slug", "jump_ts", "p_early", "p_late", "history_truncated"},
    "surprise_substantive.csv": {"slug", "jump_ts", "p_early", "p_late", "history_truncated"},
    "wallet_seed_markets.csv": {"slug", "jump_ts", "p_post", "seed_wallets", "seed_pnl",
                                "history_truncated"},
    "episode_scores.csv": {"S_final", "S_base", "M_lifetime", "M_sibling", "M_event", "M_public",
                           "post_public_share", "hours_before_public", "tier",
                           "series_bets", "series_wins", "sib_tag", "wallet", "slug",
                           "last_buy_ts", "hours_before_jump", "episode_pnl"},
    "suspicious_accounts.csv": {"rank", "wallet", "pseudonym", "max_S_final", "n_flagged"},
    "clusters.csv": {"cluster_id", "n_wallets", "wallets"},
    "event_tiers.csv": {"slug", "event", "event_type", "private_lead", "tier", "M_event"},
    "suspects_by_event.csv": {"tier", "event", "S_final", "wallet", "slug"},
    "perfect_winrate.csv": {"wallet", "n_mk", "n_won", "pnl", "inv", "win_vwap"},
    "longshot_perfect.csv": {"wallet", "n_mk", "n_won", "pnl", "inv", "win_vwap", "ret_pct"},
}


def read(out, name):
    return pd.read_csv(out / name)


def ts(s):
    return pd.Timestamp(s).timestamp()


# --- every step runs and writes what it promises -------------------------------------

@pytest.mark.parametrize("name,cols", OUTPUTS.items())
def test_outputs_exist_with_columns(pipeline_out, name, cols):
    df = read(pipeline_out, name)
    assert cols <= set(df.columns), f"{name} missing {cols - set(df.columns)}"


def test_core_outputs_not_empty(pipeline_out):
    for name in ["surprise_substantive.csv", "episode_scores.csv", "suspicious_accounts.csv",
                 "event_tiers.csv", "suspects_by_event.csv", "longshot_perfect.csv"]:
        assert len(read(pipeline_out, name)) > 0, name


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("name", sorted(OUTPUTS))
def test_outputs_are_deterministic(pipeline_out, pipeline_out_repeat, name):
    assert _digest(pipeline_out / name) == _digest(pipeline_out_repeat / name)


# --- the headline market and wallet go through the documented pipeline ---------------

def test_maduro_market_enters_through_wallet_screen(pipeline_out):
    seeds = read(pipeline_out, "wallet_seed_markets.csv").set_index("slug")
    assert MADURO in seeds.index
    assert MADURO_WALLET in seeds.loc[MADURO, "seed_wallets"]
    jump = seeds.loc[MADURO, "jump_ts"]
    assert ts("2026-01-03 09:15Z") <= jump <= ts("2026-01-03 09:30Z")


def test_maduro_wallet_tops_longshot_screen(pipeline_out):
    ls = read(pipeline_out, "longshot_perfect.csv")
    assert ls.iloc[0]["wallet"] == MADURO_WALLET
    assert ls.iloc[0]["win_vwap"] == pytest.approx(0.074, abs=0.001)


def test_maduro_wallet_is_scored(pipeline_out):
    ep = read(pipeline_out, "episode_scores.csv")
    row = ep[(ep.wallet == MADURO_WALLET) & (ep.slug == MADURO)]
    assert len(row) == 1
    row = row.iloc[0]
    gap_h = (row["jump_ts"] - row["last_buy_ts"]) / 3600
    assert gap_h >= 6.0
    assert row["vwap_entry"] == pytest.approx(0.0745, abs=0.001)
    assert row["win_buy_notional"] == pytest.approx(32538, abs=1)
    assert row["episode_pnl"] == pytest.approx(404221, abs=2)
    assert row["tier"] == "HIGH"
    assert row["sib_tag"] != "fan_bettor"


def test_maduro_wallet_is_flagged_as_fresh_bet(pipeline_out):
    row = read(pipeline_out, "episode_scores.csv").query("wallet == @MADURO_WALLET and slug == @MADURO").iloc[0]
    assert bool(row["fresh_bet"])
    assert row["wallet_age_days"] == pytest.approx(3.8, abs=0.1)
    assert row["S_final"] >= 12
    assert MADURO_WALLET in set(read(pipeline_out, "suspicious_accounts.csv")["wallet"])


def test_maduro_wallet_survives_every_control(pipeline_out):
    row = read(pipeline_out, "episode_scores.csv").query("wallet == @MADURO_WALLET and slug == @MADURO").iloc[0]
    assert row["tier"] == "HIGH"
    assert row["sib_tag"] == "targeted"
    assert row["M_public"] == 1.0
    assert row["post_public_share"] == 0
    assert row["hours_before_public"] >= 2.5
    assert row["M_lifetime"] >= 1.0


def test_news_reactions_on_maduro_market_are_demoted(pipeline_out):
    ep = read(pipeline_out, "episode_scores.csv").query("slug == @MADURO")
    after = ep[ep["post_public_share"] > 0.5]
    assert len(after) > 0
    assert (after["M_public"] < 1).all()
    assert (after.loc[after["post_public_share"] == 1, "T"] == 0).all()


def test_episode_pnl_matches_trade_tape(real_db):
    con = duckdb.connect(str(real_db), read_only=True)
    shares, cost = con.execute("""
        SELECT sum(t.size), sum(t.size * t.price) FROM trades t JOIN markets m USING (condition_id)
        WHERE m.slug = ? AND t.wallet = ? AND t.side = 'BUY' AND t.outcome_index = m.win_index""",
                               [MADURO, MADURO_WALLET]).fetchone()
    con.close()
    assert shares - cost == pytest.approx(404221, abs=2)


# --- out-of-window and excluded material ------------------------------------------------

def test_no_event_outside_window(pipeline_out):
    for name in ["surprise_markets.csv", "surprise_substantive.csv", "wallet_seed_markets.csv"]:
        j = read(pipeline_out, name)["jump_ts"]
        assert j.between(ts(config.WINDOW_START), ts(config.WINDOW_END)).all(), name


def test_cz_case_absent_everywhere(pipeline_out):
    for name in OUTPUTS:
        text = (pipeline_out / name).read_text(encoding="utf-8").lower()
        assert "changpeng" not in text, name


# --- controls are applied, not just described ----------------------------------------

def test_every_scored_event_has_an_osint_tier(pipeline_out):
    events = set(read(pipeline_out, "surprise_substantive.csv")["slug"]) |         set(read(pipeline_out, "wallet_seed_markets.csv")["slug"])
    tiers = read(pipeline_out, "event_tiers.csv")
    missing = events - set(tiers["slug"])
    assert not missing, f"events without OSINT row: {sorted(missing)}"
    assert read(pipeline_out, "episode_scores.csv")["tier"].notna().all()


def test_iran_fan_bettors_are_demoted(pipeline_out):
    ep = read(pipeline_out, "episode_scores.csv")
    iran = ep[(ep.slug == IRAN) & ep.pseudonym.isin(IRAN_FAN_BETTORS)]
    assert len(iran) >= 1
    assert (iran["sib_tag"] == "fan_bettor").all()
    assert (iran["series_bets"] >= 3).all()
    assert (iran["M_sibling"] < 1).all()


def test_final_score_applies_all_multipliers(pipeline_out):
    ep = read(pipeline_out, "episode_scores.csv")
    expected = ep.S_base * ep.M_lifetime * ep.M_sibling * ep.M_event * ep.M_public + ep.cooc_bonus
    assert (ep.S_final - expected).abs().max() < 0.01


def test_public_events_rank_below_covert_ones(pipeline_out):
    ep = read(pipeline_out, "episode_scores.csv")
    assert ep.loc[ep.tier == "LOW", "M_event"].max() < ep.loc[ep.tier == "HIGH", "M_event"].min()
