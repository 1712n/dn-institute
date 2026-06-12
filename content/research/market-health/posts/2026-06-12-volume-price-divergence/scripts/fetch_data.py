"""
Fetch real market data from Binance and CoinGecko public APIs.
No API keys required.

Data collected:
- Binance: OHLCV klines (1h) + recent trades for BTC, ETH, SOL, DOGE
- CoinGecko: Cross-exchange volume comparison
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# Binance API - OHLCV Klines
# ============================================================

BINANCE_BASE = "https://api.binance.com/api/v3"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]

def fetch_binance_klines(symbol, interval="1h", limit=1000):
    """Fetch OHLCV klines from Binance public API."""
    url = f"{BINANCE_BASE}/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_volume",
        "taker_buy_quote_volume", "ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume", "quote_volume",
                "taker_buy_volume", "taker_buy_quote_volume"]:
        df[col] = df[col].astype(float)
    df["trades"] = df["trades"].astype(int)
    df["symbol"] = symbol

    # Derived metrics
    df["price_change"] = df["close"].pct_change()
    df["abs_price_change"] = df["price_change"].abs()
    df["volume_usd"] = df["quote_volume"]
    df["avg_trade_size"] = df["volume_usd"] / df["trades"]
    df["taker_buy_ratio"] = df["taker_buy_volume"] / df["volume"]

    return df


def fetch_binance_agg_trades(symbol, limit=1000):
    """Fetch recent aggregate trades from Binance."""
    url = f"{BINANCE_BASE}/aggTrades"
    params = {
        "symbol": symbol,
        "limit": limit
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data)
    df["T"] = pd.to_datetime(df["T"], unit="ms")
    df["p"] = df["p"].astype(float)
    df["q"] = df["q"].astype(float)
    df["price"] = df["p"]
    df["qty"] = df["q"]
    df["trade_size_usd"] = df["p"] * df["q"]
    df["symbol"] = symbol

    return df


def fetch_binance_orderbook(symbol, limit=100):
    """Fetch order book snapshot from Binance."""
    url = f"{BINANCE_BASE}/depth"
    params = {
        "symbol": symbol,
        "limit": limit
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    bids = pd.DataFrame(data["bids"], columns=["price", "qty"]).astype(float)
    asks = pd.DataFrame(data["asks"], columns=["price", "qty"]).astype(float)
    bids["side"] = "bid"
    asks["side"] = "ask"

    return pd.concat([bids, asks], ignore_index=True)


# ============================================================
# CoinGecko API - Cross-exchange data
# ============================================================

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COIN_IDS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "SOLUSDT": "solana",
    "DOGEUSDT": "dogecoin"
}

def fetch_coingecko_market_chart(coin_id, days=90):
    """Fetch historical market data from CoinGecko."""
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
    prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
    volumes["timestamp"] = pd.to_datetime(volumes["timestamp"], unit="ms")

    df = prices.merge(volumes, on="timestamp")
    df["coin"] = coin_id
    return df


def fetch_coingecko_exchanges(coin_id):
    """Fetch exchange-level volume data from CoinGecko."""
    url = f"{COINGECKO_BASE}/coins/{coin_id}/tickers"
    params = {"include_exchange_logo": "false"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    tickers = []
    for t in data.get("tickers", []):
        tickers.append({
            "exchange": t["market"]["name"],
            "base": t["base"],
            "target": t["target"],
            "volume_24h": t.get("volume", 0),
            "bid_ask_spread": t.get("bid_ask_spread_percentage", 0),
            "trust_score": t.get("trust_score", "green"),
            "is_anomaly": t.get("is_anomaly", False),
            "is_stale": t.get("is_stale", False),
        })

    return pd.DataFrame(tickers)


# ============================================================
# Main execution
# ============================================================

def main():
    print("=" * 60)
    print("Fetching crypto market data for manipulation analysis")
    print("=" * 60)

    # 1. Fetch Binance klines (1h, last ~41 days = 1000 candles)
    print("\n[1/4] Fetching Binance OHLCV klines...")
    all_klines = []
    for sym in SYMBOLS:
        print(f"  -> {sym}")
        df = fetch_binance_klines(sym, interval="1h", limit=1000)
        all_klines.append(df)
        time.sleep(0.5)  # Rate limit courtesy

    klines_df = pd.concat(all_klines, ignore_index=True)
    klines_path = os.path.join(DATA_DIR, "binance_klines_1h.csv")
    klines_df.to_csv(klines_path, index=False)
    print(f"  Saved: {klines_path} ({len(klines_df)} rows)")

    # 2. Fetch Binance aggregate trades
    print("\n[2/4] Fetching Binance aggregate trades...")
    all_trades = []
    for sym in SYMBOLS:
        print(f"  -> {sym}")
        df = fetch_binance_agg_trades(sym, limit=1000)
        all_trades.append(df)
        time.sleep(0.5)

    trades_df = pd.concat(all_trades, ignore_index=True)
    trades_path = os.path.join(DATA_DIR, "binance_agg_trades.csv")
    trades_df.to_csv(trades_path, index=False)
    print(f"  Saved: {trades_path} ({len(trades_df)} rows)")

    # 3. Fetch Binance order book snapshots
    print("\n[3/4] Fetching Binance order book snapshots...")
    for sym in SYMBOLS:
        print(f"  -> {sym}")
        ob_df = fetch_binance_orderbook(sym, limit=100)
        ob_path = os.path.join(DATA_DIR, f"binance_orderbook_{sym.lower()}.csv")
        ob_df.to_csv(ob_path, index=False)
        time.sleep(0.5)

    # 4. Fetch CoinGecko data
    print("\n[4/4] Fetching CoinGecko cross-exchange data...")
    for sym, coin_id in COIN_IDS.items():
        print(f"  -> {coin_id}")
        try:
            chart_df = fetch_coingecko_market_chart(coin_id, days=90)
            chart_path = os.path.join(DATA_DIR, f"coingecko_{coin_id}_chart.csv")
            chart_df.to_csv(chart_path, index=False)

            exch_df = fetch_coingecko_exchanges(coin_id)
            exch_path = os.path.join(DATA_DIR, f"coingecko_{coin_id}_exchanges.csv")
            exch_df.to_csv(exch_path, index=False)
        except Exception as e:
            print(f"    Warning: {e}")
        time.sleep(1.5)  # CoinGecko rate limit

    print("\n" + "=" * 60)
    print("Data collection complete!")
    print(f"Files saved to: {DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
