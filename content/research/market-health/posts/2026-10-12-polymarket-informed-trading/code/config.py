import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INPUT_DIR = ROOT / "inputs"
OUTPUT_DIR = Path(os.environ.get("PM_OUTPUT_DIR", ROOT / "output"))
FIGURES_DIR = Path(os.environ.get("PM_FIGURES_DIR", OUTPUT_DIR / "figures"))
DB_PATH = Path(os.environ.get("PM_DB_PATH", DATA_DIR / "polymarket.duckdb"))

GAMMA = "https://gamma-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

USER_AGENT = "Mozilla/5.0 (research; polymarket-informed-trading)"
REQUEST_PAUSE = 0.25
MAX_RETRIES = 5

# Analysis window (resolution/endDate falls inside it).
WINDOW_START = "2025-11-01T00:00:00Z"
WINDOW_END = "2026-05-01T00:00:00Z"

POLITICS_TAG_ID = 2

# Market selection for the focused slice.
MIN_MARKET_VOLUME = 20_000
MAX_MARKET_VOLUME = 3_000_000
MAX_MARKETS = 60
TRADES_PAGE = 1000
TRADES_OFFSET_CAP = 14_000  # data-api paginates newest-first and stops ~10k
