"""Loader for Gate.io spot "deals" (trade) dumps from download.gatedata.org.

Free, key-less monthly trade dumps live at
``https://download.gatedata.org/spot/deals/{YYYYMM}/{PAIR}-{YYYYMM}.csv.gz``.

The CSV has no header; columns are:
    unix_timestamp(seconds.microseconds), trade_id, price, amount(base), side

The ``side`` flag is the taker side, encoded 1 or 2. Taker buys (side 1) push the
price up and sells (side 2) push it down, which test_side_flag_buys_push_price_up
in test_wash.py checks, so ``buy = side == 1``.
"""
import gzip
import pandas as pd
from paths import dump

BASE = "https://download.gatedata.org/spot/deals"


def load(sym, month="202605"):
    """Load one month of Gate spot trades for ``<sym>/USDT`` as a DataFrame."""
    name = f"{sym}_USDT-{month}.csv.gz"
    path = dump(f"gate/{name}", f"{BASE}/{month}/{name}")
    with gzip.open(path, "rt") as fh:
        df = pd.read_csv(fh, header=None, names=["ts", "id", "price", "amt", "side"])
    df = df.sort_values("ts").reset_index(drop=True)
    df["t"] = pd.to_datetime(df["ts"], unit="s", utc=True)
    df["buy"] = df["side"] == 1            # 1 = taker buy (verified by the uptick test)
    df["notional"] = df["price"] * df["amt"]
    return df


def load_sizes(sym, month="202605"):
    """The committed size table for ``<sym>/USDT``, written by build_sizes.py from the raw dump."""
    path = dump(f"gate/{sym}_USDT-{month}.sizes.csv.gz")
    with gzip.open(path, "rt") as fh:
        return pd.read_csv(fh, float_precision="round_trip")
