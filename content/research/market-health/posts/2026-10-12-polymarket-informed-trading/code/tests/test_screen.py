import pandas as pd
import pytest

import screen_wallets as sw
from conftest import T0, market_row, price_path, trade_row

OCT = int(pd.Timestamp("2025-09-01", tz="UTC").timestamp())


def _jump_market(cid, start):
    return (price_path(cid, start, [0.07] * 300, step=1800)
            + price_path(cid, start + 300 * 1800, [0.96] * 40, step=60))


@pytest.fixture
def screen_db(make_db):
    markets = [market_row("late", "maduro-style-late-break"),
               market_row("cz", "will-trump-pardon-changpeng-zhao-in-2025"),
               market_row("other", "other-cheap-winner"),
               market_row("lost", "lost-market", win_index=1, win_outcome="No")]
    trades = _jump_market("late", T0) + _jump_market("cz", OCT) + _jump_market("other", T0 + 86400)
    trades += price_path("lost", T0, [0.4] * 150, step=1800)
    # insider-like wallet: cheap YES on three winners
    for cid, ts in [("late", T0 + 299 * 1800), ("cz", OCT + 10), ("other", T0 + 86400 + 10)]:
        trades.append(trade_row(cid, ts, 0.05, wallet="0xlongshot", size=50_000))
    # favourite backer: perfect record, but expensive entries
    for cid, ts in [("late", T0 + 300 * 1800 + 30), ("cz", OCT + 300 * 1800 + 30),
                    ("other", T0 + 86400 + 300 * 1800 + 30)]:
        trades.append(trade_row(cid, ts, 0.96, wallet="0xfavourite", size=1_000))
    # loser: one winner, one loser
    trades.append(trade_row("other", T0 + 86400 + 20, 0.05, wallet="0xmixed", size=10_000))
    trades.append(trade_row("lost", T0 + 20, 0.4, wallet="0xmixed", size=10_000))
    trades.append(trade_row("late", T0 + 20, 0.07, wallet="0xmixed", size=10_000))
    return make_db(markets, trades)


def test_market_pnl_counts_resolution_and_sales(screen_db):
    wm = sw.wallet_market_pnl(screen_db).set_index(["wallet", "condition_id"])
    assert wm.loc[("0xlongshot", "late"), "pnl"] == pytest.approx(50_000 * 0.95)
    assert wm.loc[("0xmixed", "lost"), "pnl"] == pytest.approx(-4_000)


def test_perfect_record_requires_every_market_won(screen_db):
    perfect = sw.perfect_winrate(sw.wallet_market_pnl(screen_db))
    assert set(perfect["wallet"]) == {"0xlongshot", "0xfavourite"}
    row = perfect.set_index("wallet").loc["0xlongshot"]
    assert (row["n_mk"], row["n_won"]) == (3, 3)
    assert row["win_vwap"] == pytest.approx(0.05)


def test_longshot_screen_drops_favourite_backers(screen_db):
    perfect = sw.perfect_winrate(sw.wallet_market_pnl(screen_db))
    names = pd.DataFrame({"wallet": ["0xlongshot"], "pseudonym": [None], "name": [None]})
    lt = pd.DataFrame(columns=["wallet", "lt_markets", "lt_pnl"])
    ls = sw.longshot_perfect(perfect, names, lt)
    assert list(ls["wallet"]) == ["0xlongshot"]
    assert ls.iloc[0]["ret_pct"] == pytest.approx(1900)


def test_seed_markets_bring_late_break_and_drop_out_of_window(screen_db):
    wm = sw.wallet_market_pnl(screen_db)
    perfect = sw.perfect_winrate(wm)
    ls = sw.longshot_perfect(perfect, pd.DataFrame(columns=["wallet", "pseudonym", "name"]),
                             pd.DataFrame(columns=["wallet", "lt_markets", "lt_pnl"]))
    seeds = sw.seed_markets(screen_db, wm, ls)
    assert set(seeds["slug"]) == {"maduro-style-late-break", "other-cheap-winner"}
    late = seeds.set_index("slug").loc["maduro-style-late-break"]
    assert late["jump_ts"] == T0 + 300 * 1800
    assert late["seed_wallets"] == "0xlongshot"
