"""Build the DuckDB database the analysis reads from the committed Parquet files."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from src import tape

if __name__ == "__main__":
    tape_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else config.TAPE_DIR
    if config.DB_PATH.exists():
        sys.exit(f"{config.DB_PATH} already exists")
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    n = tape.build(tape_dir, config.DB_PATH)
    print(f"{n} trades -> {config.DB_PATH}")
