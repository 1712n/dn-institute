"""
OKX Wash Trading Analysis — data collection and metric computation.

Data source: OKX and Binance public OHLCV APIs (no API key required).
Window: 300 hourly candles ending 2026-05-11.

Metrics:
  - Pearson correlation between hourly volume and hourly price range (high-low / close %)
  - Coefficient of variation (std / mean) of hourly volume

Run:   python3 analysis.py
Deps:  requests, numpy (pip install requests numpy)
"""

import json
import pickle
from pathlib import Path

import numpy as np
import requests

PAIRS = {
    "okx_btc":  ("okx",     "BTC-USDT"),
    "bnb_btc":  ("binance", "BTCUSDT"),
    "okx_eth":  ("okx",     "ETH-USDT"),
    "bnb_eth":  ("binance", "ETHUSDT"),
    "okx_okb":  ("okx",     "OKB-USDT"),
}

CACHE = Path(__file__).parent / "candle_data.pkl"


def fetch_okx(inst_id: str, limit: int = 300) -> list[dict]:
    candles = []
    after = ""
    while len(candles) < limit:
        params = {"instId": inst_id, "bar": "1H", "limit": 100}
        if after:
            params["after"] = after
        r = requests.get("https://www.okx.com/api/v5/market/history-candles", params=params, timeout=15)
        r.raise_for_status()
        batch = r.json()["data"]
        if not batch:
            break
        for c in batch:
            ts, o, h, l, close, vol = c[0], c[1], c[2], c[3], c[4], c[5]
            candles.append({"ts": int(ts), "open": float(o), "high": float(h),
                            "low": float(l), "close": float(close), "vol": float(vol)})
        after = batch[-1][0]
    return candles[:limit]


def fetch_binance(symbol: str, limit: int = 300) -> list[dict]:
    candles = []
    end_time = None
    while len(candles) < limit:
        params = {"symbol": symbol, "interval": "1h", "limit": min(1000, limit - len(candles))}
        if end_time:
            params["endTime"] = end_time
        r = requests.get("https://api.binance.com/api/v3/klines", params=params, timeout=15)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for c in batch:
            candles.append({"ts": c[0], "open": float(c[1]), "high": float(c[2]),
                            "low": float(c[3]), "close": float(c[4]), "vol": float(c[5])})
        end_time = batch[0][0] - 1
    return sorted(candles, key=lambda x: x["ts"])[:limit]


def load_or_fetch() -> dict:
    if CACHE.exists():
        print(f"Loading cached data from {CACHE.name}")
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    print("Fetching live data from OKX and Binance APIs...")
    data = {}
    for key, (exchange, symbol) in PAIRS.items():
        print(f"  {key}...")
        data[key] = fetch_okx(symbol) if exchange == "okx" else fetch_binance(symbol)
    with open(CACHE, "wb") as f:
        pickle.dump(data, f)
    return data


def compute(candles: list[dict]) -> tuple[float, float]:
    vol = np.array([c["vol"] for c in candles])
    rng = np.array([(c["high"] - c["low"]) / c["close"] * 100 for c in candles])
    r = float(np.corrcoef(vol, rng)[0, 1])
    cv = float(vol.std() / vol.mean())
    return r, cv


def main():
    data = load_or_fetch()

    print(f"\n{'Exchange':<10} {'Pair':<12} {'r (vol~volatility)':>20} {'CV (vol)':>10}")
    print("-" * 56)
    labels = {
        "okx_btc": ("OKX",     "BTC/USDT"),
        "bnb_btc": ("Binance", "BTC/USDT"),
        "okx_eth": ("OKX",     "ETH/USDT"),
        "bnb_eth": ("Binance", "ETH/USDT"),
        "okx_okb": ("OKX",     "OKB/USDT"),
    }
    for key, (exchange, pair) in labels.items():
        if key in data:
            r, cv = compute(data[key])
            print(f"{exchange:<10} {pair:<12} {r:>20.3f} {cv:>10.3f}")


if __name__ == "__main__":
    main()
