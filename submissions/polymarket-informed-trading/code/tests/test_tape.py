import duckdb

from conftest import market_row, trade_row
from src import tape

COLS = "condition_id, wallet, side, size, price, timestamp, outcome_index, pseudonym, name, bio"


def _sample():
    markets = [market_row("0xa", "market-a"), market_row("0xb", "market-b", win_index=1),
               market_row("0xc", "market-c")]
    trades = [
        trade_row("0xa", 100, 0.0385405961, wallet="0x1", size=31.136, pseudonym="Odd-Fill"),
        trade_row("0xa", 100, 0.07, wallet="0x2", side="SELL", size=0.000001),
        trade_row("0xa", 200, 0.988281558, wallet="0x1", size=106.55, pseudonym="Odd-Fill"),
        trade_row("0xb", 300, 0.004, wallet="0x3", outcome_index=1, size=33.86, pseudonym="Old"),
        # the same wallet changed its profile between trades
        trade_row("0xb", 400, 0.995, wallet="0x3", outcome_index=1, size=20.0, pseudonym="New"),
        trade_row("0xc", 500, 0.5, wallet="0x2", size=1e6),
        # one second, two transactions: the hash, not the wallet, sets the order
        trade_row("0xc", 600, 0.6, wallet="0x1", size=5.0, pseudonym="Odd-Fill"),
        trade_row("0xc", 600, 0.4, wallet="0x2", size=5.0),
        # one second, one transaction with two fills
        trade_row("0xc", 700, 0.6, wallet="0x2", size=1.0),
        trade_row("0xc", 700, 0.6, wallet="0x3", size=2.0, pseudonym="New"),
    ]
    hashes = {(600, "0x1"): "0xbb" + "1" * 62, (600, "0x2"): "0xaa" + "2" * 62,
              (700, "0x2"): "0xcc" + "3" * 62, (700, "0x3"): "0xcc" + "3" * 62}
    for t in trades:
        t["tx_hash"] = hashes.get((t["timestamp"], t["wallet"]), "0x" + "f" * 64)
    return markets, trades


def _rows(con):
    return con.execute(f"SELECT {COLS} FROM trades ORDER BY ALL").fetchall()


def _tape_order(con):
    # the order detect_surprises.py and make_figures.py read the tape in
    return con.execute("SELECT condition_id, wallet, timestamp FROM trades ORDER BY condition_id, "
                       "timestamp, tx_hash, wallet, price, size").fetchall()


def test_roundtrip_restores_every_trade(make_db, tmp_path):
    src = make_db(*_sample())
    n_parts = tape.pack(src, tmp_path / "tape", part_rows=3)
    assert n_parts == 3  # whole markets per file: 0xa, 0xb, 0xc
    n = tape.build(tmp_path / "tape", tmp_path / "rebuilt.duckdb")
    assert n == 10
    out = duckdb.connect(str(tmp_path / "rebuilt.duckdb"), read_only=True)
    assert _rows(out) == _rows(src)
    assert _tape_order(out) == _tape_order(src)
    hashes = out.execute("SELECT DISTINCT tx_hash FROM trades ORDER BY ALL").fetchall()
    assert hashes == [("0xaa222222",), ("0xbb111111",), (None,)]
    assert out.execute("SELECT * FROM markets ORDER BY condition_id").fetchall() == \
        src.execute("SELECT * FROM markets ORDER BY condition_id").fetchall()


def test_profiles_stored_once_per_version(make_db, tmp_path):
    tape.pack(make_db(*_sample()), tmp_path / "tape")
    w = duckdb.sql(f"SELECT wallet, pseudonym FROM read_parquet('{(tmp_path / 'tape').as_posix()}"
                   "/wallets.parquet') ORDER BY ALL").fetchall()
    assert w == [("0x1", "Odd-Fill"), ("0x2", None), ("0x3", "New"), ("0x3", "Old")]


def test_pack_replaces_old_files(make_db, tmp_path):
    out = tmp_path / "tape"
    out.mkdir()
    (out / "trades_9.parquet").write_bytes(b"stale")
    tape.pack(make_db(*_sample()), out)
    assert not (out / "trades_9.parquet").exists()


def test_paths_with_quotes(make_db, tmp_path):
    folder = tmp_path / "o'brien"
    src = make_db(*_sample())
    tape.pack(src, folder / "tape")
    assert tape.build(folder / "tape", folder / "rebuilt.duckdb") == 10
    out = duckdb.connect(str(folder / "rebuilt.duckdb"), read_only=True)
    assert _rows(out) == _rows(src)


class _FailOn:
    """Connection that raises on the first statement containing `marker`."""

    def __init__(self, con, marker):
        self.con, self.marker = con, marker

    def execute(self, sql, *args):
        if self.marker in sql:
            raise duckdb.IOException("disk full")
        return self.con.execute(sql, *args)


def test_failed_pack_keeps_the_old_tape(make_db, tmp_path):
    out = tmp_path / "tape"
    src = make_db(*_sample())
    tape.pack(src, out, part_rows=3)
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    try:
        tape.pack(_FailOn(src, "trades_2.parquet"), out, part_rows=3)
    except duckdb.IOException:
        pass
    else:
        raise AssertionError("the injected failure did not happen")
    assert {p.name: p.read_bytes() for p in out.iterdir()} == before
    # no half-written folder left next to the tape
    db_files = {"synthetic.duckdb", "synthetic.duckdb.wal"}
    assert {p.name for p in tmp_path.iterdir()} - db_files == {"tape"}
    # the same connection can pack again: no temporary tables left behind
    tape.pack(src, out, part_rows=3)
    assert {p.name: p.read_bytes() for p in out.iterdir()} == before
