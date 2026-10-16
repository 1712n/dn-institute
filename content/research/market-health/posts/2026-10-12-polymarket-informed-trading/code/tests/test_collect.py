import io
import json

import duckdb
import pandas as pd
import pytest

import config
from src import collect, pm_client, trace


class _Resp:
    def __init__(self, status, payload=None):
        self.status_code = status
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(pm_client.time, "sleep", lambda s: None)
    monkeypatch.setattr(trace.time, "sleep", lambda s: None)


def _client(monkeypatch, statuses):
    c = pm_client.PolymarketClient()
    answers = iter(statuses)
    monkeypatch.setattr(c.s, "get", lambda *a, **k: next(answers))
    return c


def test_exhausted_retries_raise(monkeypatch):
    c = _client(monkeypatch, [_Resp(429)] * config.MAX_RETRIES)
    with pytest.raises(RuntimeError, match="429"):
        c._get("https://example.org/trades")


def test_retry_then_success(monkeypatch):
    c = _client(monkeypatch, [_Resp(503), _Resp(200, [{"a": 1}])])
    assert c._get("https://example.org/trades") == [{"a": 1}]


def test_rejected_request_is_end_of_list(monkeypatch):
    c = _client(monkeypatch, [_Resp(400)])
    assert c._get("https://example.org/trades") is None


class _Pages:
    def __init__(self, pages):
        self.pages = list(pages)

    def trades_page(self, condition_id, offset):
        return self.pages.pop(0) if self.pages else []


def _trade(i, outcome=0):
    t = {"proxyWallet": f"0x{i}", "side": "BUY", "size": 1, "price": 0.5, "timestamp": i,
         "transactionHash": None}
    if outcome is not None:
        t["outcomeIndex"] = outcome
    return t


def test_trade_without_outcome_index_is_dropped():
    tdf, capped = collect.fetch_trades(_Pages([[_trade(1, 0), _trade(2, None), _trade(3, 1)]]), "c")
    assert list(tdf["wallet"]) == ["0x1", "0x3"]
    assert list(tdf["outcome_index"]) == [0, 1]
    assert not capped


def test_failed_market_is_left_for_the_next_run(tmp_path, monkeypatch):
    db = tmp_path / "pm.duckdb"
    con = duckdb.connect(str(db))
    con.register("u", pd.DataFrame({"condition_id": ["ok", "bad"], "slug": ["ok", "bad"],
                                    "volume": [10.0, 5.0]}))
    con.execute("CREATE TABLE universe AS SELECT * FROM u")
    con.close()

    real_fetch = collect.fetch_trades

    def fake_fetch(client, cid):
        if cid == "bad":
            raise RuntimeError("HTTP 429 after 5 attempts")
        return real_fetch(_Pages([[_trade(1)]]), cid)

    monkeypatch.setattr(collect, "fetch_trades", fake_fetch)
    collect.run_full_parallel(db_path=db, workers=2, verbose=False)
    con = duckdb.connect(str(db), read_only=True)
    assert con.execute("SELECT condition_id FROM collected").fetchall() == [("ok",)]
    assert con.execute("SELECT count(*) FROM trades").fetchone()[0] == 1
    con.close()


def test_failed_insert_rolls_back(tmp_path):
    con = duckdb.connect(str(tmp_path / "pm.duckdb"))
    con.execute(collect._TRADES_DDL)
    con.execute("CREATE TABLE collected(condition_id VARCHAR, n_trades INTEGER)")  # wrong shape
    tdf, capped = collect.fetch_trades(_Pages([[_trade(1)]]), "c")
    with pytest.raises(duckdb.Error):
        collect._store(con, "c", tdf, capped)
    assert con.execute("SELECT count(*) FROM trades").fetchone()[0] == 0


def _etherscan(monkeypatch, payloads):
    answers = iter(payloads)
    monkeypatch.setattr(trace.urllib.request, "urlopen",
                        lambda *a, **k: io.BytesIO(json.dumps(next(answers)).encode()))


def test_etherscan_empty_history(monkeypatch):
    _etherscan(monkeypatch, [{"status": "0", "message": "No transactions found", "result": []}])
    assert trace._get({"action": "txlist"}) == []
    _etherscan(monkeypatch, [{"status": "0", "message": "No transactions found", "result": "x"}])
    assert trace._get({"action": "txlist"}) == []


def test_etherscan_error_raises(monkeypatch):
    _etherscan(monkeypatch, [{"status": "0", "message": "NOTOK", "result": "Invalid API Key"}])
    with pytest.raises(RuntimeError, match="Invalid API Key"):
        trace._get({"action": "txlist"})
