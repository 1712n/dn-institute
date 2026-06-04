#!/usr/bin/env python3
"""Recompute the Binance CRV/USDT statistics used by index.md."""
from __future__ import annotations
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def read_csv(name: str):
    with (ROOT / name).open(newline="") as fh:
        return list(csv.DictReader(fh))

daily = read_csv("crv-usdt-binance-daily.csv")
hourly = read_csv("crv-usdt-binance-hourly.csv")
prior = [float(r["quote_volume_usdt"]) for r in daily if "2022-11-15" <= r["date"] <= "2022-11-21"]
nov22 = next(r for r in daily if r["date"] == "2022-11-22")
nov22_quote = float(nov22["quote_volume_usdt"])
prior_avg = sum(prior) / len(prior)
range_low = (float(nov22["high"]) - float(nov22["low"])) / float(nov22["low"]) * 100
nov22_hours = [r for r in hourly if r["open_time_utc"].startswith("2022-11-22")]
hourly_quote = sum(float(r["quote_volume_usdt"]) for r in nov22_hours)
hourly_base = sum(float(r["base_volume_crv"]) for r in nov22_hours)
hourly_trades = sum(int(r["trade_count"]) for r in nov22_hours)
prior_hourly = [
    float(r["quote_volume_usdt"])
    for r in hourly
    if r["open_time_utc"].startswith("2022-11-20") or r["open_time_utc"].startswith("2022-11-21")
]
prior_hourly_avg = sum(prior_hourly) / len(prior_hourly)
peak_hour = max(nov22_hours, key=lambda r: float(r["quote_volume_usdt"]))
peak_hour_quote = float(peak_hour["quote_volume_usdt"])
peak_hour_taker_buy = float(peak_hour["taker_buy_quote_volume_usdt"])
peak_hour_taker_sell = peak_hour_quote - peak_hour_taker_buy
print(f"prior_week_avg_quote_volume_usdt={prior_avg:.6f}")
print(f"nov22_quote_volume_usdt={nov22_quote:.6f}")
print(f"volume_multiple={nov22_quote / prior_avg:.6f}")
print(f"nov22_high_low_range_pct_low_denominator={range_low:.6f}")
print(f"nov22_hourly_quote_sum_usdt={hourly_quote:.6f}")
print(f"nov22_hourly_base_sum_crv={hourly_base:.6f}")
print(f"nov22_hourly_trade_count_sum={hourly_trades}")
print(f"peak_hour={peak_hour['open_time_utc']} quote_volume_usdt={peak_hour_quote:.6f}")
print(f"peak_hour_vs_nov20_21_hourly_avg={peak_hour_quote / prior_hourly_avg:.6f}")
print(f"peak_hour_taker_sell_quote_volume_usdt={peak_hour_taker_sell:.6f}")
print(f"peak_hour_taker_sell_share={peak_hour_taker_sell / peak_hour_quote:.6f}")
