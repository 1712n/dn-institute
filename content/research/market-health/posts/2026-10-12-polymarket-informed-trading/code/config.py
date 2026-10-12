from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DB_PATH = DATA_DIR / "polymarket.duckdb"

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

# Heuristic thresholds (documented in report/REPORT.md).
MIN_WIN_NOTIONAL = 500.0        # ignore dust winning positions
CHEAP_ENTRY = 0.35              # vwap entry on winning side considered "long odds"
VERY_CHEAP_ENTRY = 0.15
PRE_MOVE_PRICE = 0.20           # price level below which the crowd disbelieved the outcome
FWD_HORIZON_H = 24              # forward-return horizon in hours
PRE_RES_HOURS = 72             # "near resolution" window before endDate

# Gates for the ranking.
MIN_WALLET_NOTIONAL = 500.0
MIN_WALLET_TRADES = 2
