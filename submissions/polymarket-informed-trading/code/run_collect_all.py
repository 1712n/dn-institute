import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import collect

if __name__ == "__main__":
    collect.run_full_parallel(min_volume=1.0, workers=16, verbose=True)
