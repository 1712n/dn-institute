"""The trade database as Parquet files small enough to commit, and back.

Wallet addresses and profiles are stored once in wallets.parquet and referenced by number from
the trades. Prices and sizes are kept as integers (price x 1e10, size x 1e6), which restores the
API values exactly. Full transaction hashes would take most of the space, and the analysis only
uses them to order trades of one market made in the same second; they are kept for those trades
only, cut to their first 8 hex digits, which orders them the same way.
"""
import shutil
import tempfile
from pathlib import Path

import duckdb

PART_ROWS = 4_500_000  # about 45 MB per trades file
TX_PREFIX = 10         # "0x" + 8 hex digits
PARQUET = "FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 19, ROW_GROUP_SIZE 1000000"


def _sql_path(path):
    """A path as an SQL string literal."""
    return "'" + Path(path).as_posix().replace("'", "''") + "'"


def pack(con, out_dir, part_rows=PART_ROWS):
    """Write the files to a folder next to `out_dir` and swap them in only once all are written,
    so a failed export leaves the previous tape as it was."""
    out = Path(out_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        n = _write(con, tmp, part_rows)
        out.mkdir(exist_ok=True)
        for old in out.glob("*.parquet"):
            old.unlink()
        for new in tmp.iterdir():
            new.replace(out / new.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return n


def _write(con, out, part_rows):
    try:
        return _write_files(con, out, part_rows)
    finally:
        con.execute("DROP TABLE IF EXISTS profiles")
        con.execute("DROP TABLE IF EXISTS shared_second")


def _write_files(con, out, part_rows):
    con.execute(f"COPY (SELECT * FROM markets ORDER BY condition_id) "
                f"TO {_sql_path(out / 'markets.parquet')} ({PARQUET})")
    con.execute("""
        CREATE TEMP TABLE profiles AS
        SELECT (row_number() OVER (ORDER BY wallet, pseudonym, "name", bio) - 1)::INTEGER pid,
               wallet, pseudonym, "name", bio
        FROM (SELECT DISTINCT wallet, pseudonym, "name", bio FROM trades)""")
    con.execute(f"COPY (SELECT * FROM profiles ORDER BY pid) "
                f"TO {_sql_path(out / 'wallets.parquet')} ({PARQUET})")
    con.execute("""
        CREATE TEMP TABLE shared_second AS
        SELECT condition_id, timestamp FROM trades
        GROUP BY 1, 2 HAVING count(DISTINCT tx_hash) > 1""")
    # whole markets per file, in condition_id order
    counts = con.execute(
        "SELECT condition_id, count(*) n FROM trades GROUP BY 1 ORDER BY 1").fetchall()
    parts, cur, n = [], [], 0
    for cid, k in counts:
        if cur and n + k > part_rows:
            parts.append(cur)
            cur, n = [], 0
        cur.append(cid)
        n += k
    if cur:
        parts.append(cur)
    for i, cids in enumerate(parts, 1):
        con.execute(f"""
            COPY (SELECT t.condition_id, p.pid, t.side = 'BUY' buy,
                         t.outcome_index::UTINYINT outcome_index,
                         round(t.price * 1e10)::BIGINT price_e10,
                         round(t.size * 1e6)::BIGINT size_e6, t.timestamp,
                         CASE WHEN s.timestamp IS NOT NULL THEN left(t.tx_hash, {TX_PREFIX}) END tx
                  FROM trades t
                  JOIN profiles p ON p.wallet = t.wallet
                   AND p.pseudonym IS NOT DISTINCT FROM t.pseudonym
                   AND p."name" IS NOT DISTINCT FROM t."name"
                   AND p.bio IS NOT DISTINCT FROM t.bio
                  LEFT JOIN shared_second s USING (condition_id, timestamp)
                  WHERE t.condition_id BETWEEN ? AND ?
                  ORDER BY t.condition_id, t.timestamp, tx, p.pid, price_e10, size_e6)
            TO {_sql_path(out / f'trades_{i}.parquet')} ({PARQUET})""", [cids[0], cids[-1]])
    return len(parts)


def build(tape_dir, db_path):
    tape = Path(tape_dir)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE TABLE markets AS "
                f"SELECT * FROM read_parquet({_sql_path(tape / 'markets.parquet')})")
    con.execute(f"""
        CREATE TABLE trades AS
        SELECT t.condition_id, w.wallet, CASE WHEN t.buy THEN 'BUY' ELSE 'SELL' END side,
               t.size_e6 / 1e6 size, t.price_e10 / 1e10 price, t.timestamp,
               t.outcome_index::INTEGER outcome_index, t.tx tx_hash, w.pseudonym, w."name", w.bio
        FROM read_parquet({_sql_path(tape / 'trades_*.parquet')}) t
        JOIN read_parquet({_sql_path(tape / 'wallets.parquet')}) w USING (pid)
        ORDER BY t.condition_id, t.timestamp, t.tx, t.pid, t.price_e10, t.size_e6""")
    n = con.execute("SELECT count(*) FROM trades").fetchone()[0]
    con.close()
    return n
