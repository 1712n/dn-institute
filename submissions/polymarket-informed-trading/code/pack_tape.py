"""Write the trade database to data/tape/ as Parquet files (see src/tape.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb

import config
from src import tape

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else config.TAPE_DIR
    con = duckdb.connect(str(config.DB_PATH), read_only=True)
    n = tape.pack(con, out)
    con.close()
    print(f"{n} trade files in {out}")
