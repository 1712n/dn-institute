import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import config  # noqa: E402

PIPELINE = [
    ["detect_surprises.py"],
    ["screen_wallets.py", "--offline"],
    ["run_account_phase.py", "--offline"],
    ["build_artifacts.py"],
    ["make_figures.py"],
]

MARKET_COLS = ["condition_id", "slug", "question", "event_slug", "start_date", "end_date",
               "volume", "outcomes", "win_index", "win_outcome", "token_win", "token_lose",
               "resolved_by", "n_trades", "trades_capped"]
TRADE_COLS = ["condition_id", "wallet", "side", "size", "price", "timestamp", "outcome_index",
              "tx_hash", "pseudonym", "name", "bio"]

T0 = int(pd.Timestamp("2026-01-01", tz="UTC").timestamp())


def market_row(cid, slug, event_slug=None, win_index=0, win_outcome="Yes", volume=100_000):
    return {"condition_id": cid, "slug": slug, "question": slug, "event_slug": event_slug or slug,
            "start_date": "2025-10-01T00:00:00Z", "end_date": "2026-03-31T12:00:00Z",
            "volume": volume, "outcomes": '["Yes", "No"]', "win_index": win_index,
            "win_outcome": win_outcome, "token_win": None, "token_lose": None,
            "resolved_by": None, "n_trades": 0, "trades_capped": False}


def trade_row(cid, ts, price, wallet="0xcrowd", side="BUY", size=100.0, outcome_index=0,
              pseudonym=None):
    return {"condition_id": cid, "wallet": wallet, "side": side, "size": size, "price": price,
            "timestamp": int(ts), "outcome_index": outcome_index, "tx_hash": None,
            "pseudonym": pseudonym, "name": None, "bio": None}


def price_path(cid, start_ts, prices, step=600, **kw):
    return [trade_row(cid, start_ts + i * step, p, **kw) for i, p in enumerate(prices)]


@pytest.fixture
def make_db(tmp_path):
    def build(markets, trades):
        path = tmp_path / "synthetic.duckdb"
        con = duckdb.connect(str(path))
        m = pd.DataFrame(markets, columns=MARKET_COLS)
        t = pd.DataFrame(trades, columns=TRADE_COLS)
        m["n_trades"] = m["condition_id"].map(t.groupby("condition_id").size()).fillna(0).astype(int)
        con.register("m_df", m)
        con.register("t_df", t)
        con.execute("CREATE TABLE markets AS SELECT * FROM m_df")
        con.execute("CREATE TABLE trades AS SELECT * FROM t_df")
        con.close()
        return duckdb.connect(str(path), read_only=True)
    return build


def _run_pipeline(out_dir):
    env = {**os.environ, "PM_OUTPUT_DIR": str(out_dir), "PYTHONIOENCODING": "utf-8",
           "MPLBACKEND": "Agg"}
    for step in PIPELINE:
        r = subprocess.run([sys.executable, *step], cwd=ROOT, env=env,
                           capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, f"{step[0]} failed:\n{r.stdout[-2000:]}\n{r.stderr[-4000:]}"
    return out_dir


@pytest.fixture(scope="session")
def real_db():
    if not config.DB_PATH.exists():
        pytest.skip("polymarket.duckdb is not available")
    return config.DB_PATH


@pytest.fixture(scope="session")
def pipeline_out(real_db, tmp_path_factory):
    return _run_pipeline(tmp_path_factory.mktemp("run1"))


@pytest.fixture(scope="session")
def pipeline_out_repeat(real_db, pipeline_out, tmp_path_factory):
    return _run_pipeline(tmp_path_factory.mktemp("run2"))
