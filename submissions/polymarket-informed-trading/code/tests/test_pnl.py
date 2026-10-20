import pandas as pd
import pytest

import run_account_phase as rap
from conftest import T0, market_row, price_path, trade_row


def _sells(*pairs):
    return pd.DataFrame(pairs, columns=["size", "price"])


def test_held_position_pays_out_at_resolution():
    assert rap.realized_pnl(1_000, 100.0, _sells()) == pytest.approx(900)


def test_partial_sale_counts_at_sale_price():
    # 400 sold at 50c, 600 held to $1
    assert rap.realized_pnl(1_000, 100.0, _sells((400, 0.5))) == pytest.approx(200 + 600 - 100)


def test_sales_are_matched_first_in_first_out():
    # the first 1,000 sold at 50c close the episode; the later 500 at 80c belong to later buys
    pnl = rap.realized_pnl(1_000, 100.0, _sells((1_000, 0.5), (500, 0.8)))
    assert pnl == pytest.approx(1_000 * 0.5 - 100)


def test_sale_straddling_the_episode_is_split():
    # 800 at 40c, then 400 at 90c of which only 200 belong to the episode
    pnl = rap.realized_pnl(1_000, 100.0, _sells((800, 0.4), (400, 0.9)))
    assert pnl == pytest.approx(800 * 0.4 + 200 * 0.9 - 100)


@pytest.fixture
def episode_db(make_db):
    markets = [market_row("m", "jump-market")]
    trades = price_path("m", T0, [0.1] * 20, step=600)
    w = "0xseller"
    trades.append(trade_row("m", T0 + 50, 0.9, wallet=w, side="SELL", size=300))   # before its first buy
    trades.append(trade_row("m", T0 + 100, 0.1, wallet=w, size=1_000))
    trades.append(trade_row("m", T0 + 20_000, 0.5, wallet=w, side="SELL", size=400))
    trades.append(trade_row("m", T0 + 20_100, 0.6, wallet=w, side="SELL", size=100, outcome_index=1))
    trades.append(trade_row("m", T0 + 200, 0.1, wallet="0xholder", size=2_000))
    # bought 1,000 before the jump, then 1,000 more after it, and sold 1,500 late at 95c
    v = "0xrebuyer"
    trades.append(trade_row("m", T0 + 300, 0.1, wallet=v, size=1_000))
    trades.append(trade_row("m", T0 + 20_000, 0.3, wallet=v, side="SELL", size=500))
    trades.append(trade_row("m", T0 + 20_500, 0.9, wallet=v, size=1_000))
    trades.append(trade_row("m", T0 + 21_000, 0.95, wallet=v, side="SELL", size=1_500))
    return make_db(markets, trades)


def test_episode_keeps_payoff_and_adds_realized_profit(episode_db):
    tg = pd.DataFrame({"condition_id": ["m"], "slug": ["jump-market"], "source": ["price"],
                       "win_index": [0], "jump_ts": [T0 + 10_000], "p_late": [0.96],
                       "public_ts": [T0 + 10_000]})
    ep = rap.episodes(episode_db, tg).set_index("wallet")
    assert ep.loc["0xseller", "episode_pnl"] == pytest.approx(900)
    # the sale before the first buy and the sale of the other outcome are ignored
    assert ep.loc["0xseller", "realized_pnl"] == pytest.approx(400 * 0.5 + 600 - 100)
    assert ep.loc["0xholder", "realized_pnl"] == pytest.approx(ep.loc["0xholder", "episode_pnl"])
    # the post-jump buy and its sale do not raise the episode's profit
    assert ep.loc["0xrebuyer", "realized_pnl"] == pytest.approx(500 * 0.3 + 500 * 0.95 - 100)
