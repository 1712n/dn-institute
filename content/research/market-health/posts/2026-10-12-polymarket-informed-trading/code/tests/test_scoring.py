import numpy as np
import pandas as pd

import run_account_phase as rap


def test_record_excludes_the_scored_market():
    bets = pd.DataFrame({"wallet": ["w", "w", "w", "v"],
                         "condition_id": ["A", "B", "C", "A"],
                         "won": [True, False, True, True]})
    ep = pd.DataFrame({"wallet": ["w", "v", "u"], "condition_id": ["A", "A", "A"]})
    out = rap.record_excluding_own(ep, bets).set_index("wallet")
    assert (out.loc["w", "attempts"], out.loc["w", "wins"]) == (2, 1)
    assert (out.loc["v", "attempts"], out.loc["v", "wins"]) == (0, 0)
    assert (out.loc["u", "attempts"], out.loc["u", "wins"]) == (0, 0)


def test_record_keeps_other_markets_when_own_market_absent():
    bets = pd.DataFrame({"wallet": ["w", "w"], "condition_id": ["B", "C"], "won": [True, True]})
    ep = pd.DataFrame({"wallet": ["w"], "condition_id": ["A"]})
    out = rap.record_excluding_own(ep, bets).iloc[0]
    assert (out["attempts"], out["wins"]) == (2, 2)


def _flagged(pseudonyms):
    n = len(pseudonyms)
    return pd.DataFrame({
        "wallet": [f"0x{i}" for i in range(n)], "pseudonym": pseudonyms,
        "S_final": np.linspace(20, 30, n), "S_base": 10.0, "slug": "m",
        "win_buy_notional": 1000.0, "episode_pnl": 5000.0, "realized_pnl": 5000.0, "M_lifetime": 1.0,
        "M_sibling": 1.0, "M_event": 1.0, "M_public": 1.0, "lt_markets": 1, "lt_pnl": 0.0, "lt_tag": "fresh",
        "in_cluster": False, "cluster_id": np.nan, "wins": 0, "attempts": 0,
        "sib_tag": "standalone", "tier": "HIGH",
    })


def test_wallets_without_pseudonym_are_ranked():
    wal = rap.rank_wallets(_flagged(["Named-Trader", None, np.nan]))
    assert len(wal) == 3
    assert set(wal["wallet"]) == {"0x0", "0x1", "0x2"}


def test_rank_wallets_orders_by_markets_then_profit():
    fl = _flagged(["a", "b", "c"]).assign(realized_pnl=[9000.0, 1000.0, 400000.0])
    fl = pd.concat([fl, fl.iloc[[1]].assign(slug="n")], ignore_index=True)
    wal = rap.rank_wallets(fl)
    assert list(wal["pseudonym"]) == ["b", "c", "a"]
    assert list(wal["rank"]) == [1, 2, 3]


def test_rank_wallets_uses_realized_profit_not_payoff():
    # "a" would have been paid more had it held, but sold early
    fl = _flagged(["a", "b"]).assign(episode_pnl=[30000.0, 10000.0], realized_pnl=[8000.0, 10000.0])
    wal = rap.rank_wallets(fl)
    assert list(wal["pseudonym"]) == ["b", "a"]
    assert list(wal["tot_realized_pnl"]) == [10000.0, 8000.0]
    assert list(wal["tot_episode_pnl"]) == [10000.0, 30000.0]
