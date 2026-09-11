#!/usr/bin/env python3
"""Reconstruct a fixed historical USDe event from checksum-verified public archives.

No API keys, accounts, order submission, or live exchange access are used.
"""

import collections
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import zipfile


ROOT = Path(__file__).resolve().parent
EVENT = "2025-10-10"
UTC = dt.timezone.utc


def iso(microseconds):
    return dt.datetime.fromtimestamp(microseconds // 1_000_000, UTC).replace(
        microsecond=microseconds % 1_000_000).isoformat().replace("+00:00", "Z")


def epoch(day, hour=0, minute=0):
    return int(dt.datetime.fromisoformat(day).replace(
        hour=hour, minute=minute, tzinfo=UTC).timestamp()) * 1_000_000


def csv_rows(spec):
    path = ROOT / "raw" / spec["local_file"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
        raise ValueError(f"Input hash changed: {path}")
    with zipfile.ZipFile(path) as archive:
        with archive.open(spec["csv_member"]) as stream:
            yield from csv.reader(io.TextIOWrapper(stream, encoding="utf-8"))


def load_trades(spec):
    records = []
    previous_id = None
    previous_ts = None
    previous_last_trade_id = None
    first_ts = epoch(spec["date"])
    gaps = 0
    for row in csv_rows(spec):
        if len(row) != 8 or row[6] not in ("True", "False") or row[7] not in ("True", "False"):
            raise ValueError(f"Unexpected aggTrades format: {spec['local_file']}")
        ident, price, quantity, first, last, ts = (
            int(row[0]), float(row[1]), float(row[2]), int(row[3]), int(row[4]), int(row[5]))
        if not (math.isfinite(price) and math.isfinite(quantity) and price > 0 and quantity > 0):
            raise ValueError("Nonpositive or nonfinite price/quantity")
        if not (first_ts <= ts < first_ts + 86_400_000_000) or first > last:
            raise ValueError("Timestamp outside source day or invalid underlying trade range")
        if previous_id is not None:
            if ident <= previous_id or ts < previous_ts or first <= previous_last_trade_id:
                raise ValueError("Nonmonotonic IDs/timestamps or overlapping underlying trades")
            gaps += ident - previous_id - 1
        records.append({"id": ident, "price": price, "quantity": quantity,
                        "notional": price * quantity, "first_trade_id": first,
                        "last_trade_id": last, "underlying_trades": last - first + 1,
                        "timestamp_us": ts, "taker_buy": row[6] == "False"})
        previous_id, previous_ts, previous_last_trade_id = ident, ts, last
    if not records:
        raise ValueError(f"Empty input: {spec['local_file']}")
    return records, gaps


def summarize(records):
    if not records:
        return {"aggregate_records": 0, "underlying_trades": 0, "base_volume": 0,
                "quote_notional": 0, "vwap": None, "low": None, "high": None,
                "open": None, "close": None, "taker_sell_base_share": None,
                "taker_sell_quote_share": None}
    quantity = math.fsum(r["quantity"] for r in records)
    notional = math.fsum(r["notional"] for r in records)
    return {"aggregate_records": len(records),
            "underlying_trades": sum(r["underlying_trades"] for r in records),
            "base_volume": quantity, "quote_notional": notional,
            "vwap": notional / quantity,
            "low": min(r["price"] for r in records), "high": max(r["price"] for r in records),
            "open": records[0]["price"], "close": records[-1]["price"],
            "taker_sell_base_share": math.fsum(r["quantity"] for r in records if not r["taker_buy"]) / quantity,
            "taker_sell_quote_share": math.fsum(r["notional"] for r in records if not r["taker_buy"]) / notional}


def window(records, start, end):
    return [r for r in records if start <= r["timestamp_us"] < end]


def write_csv(name, records):
    if not records:
        raise ValueError(f"Refusing empty output {name}")
    with (ROOT / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main():
    manifest = json.loads((ROOT / "source_manifest.json").read_text())
    all_trades, minute_rows, daily_rows, input_checks = {}, [], [], []
    klines = {}
    for spec in manifest["archives"]:
        if spec["kind"] != "aggTrades":
            data = list(csv_rows(spec))
            if len(data) != 1440 or any(len(r) != 12 for r in data):
                raise ValueError("Expected 1440 twelve-column one-minute kline rows")
            expected_times = range(epoch(spec["date"]), epoch(spec["date"]) + 86_400_000_000, 60_000_000)
            if [int(r[0]) for r in data] != list(expected_times):
                raise ValueError("Missing, duplicate or misordered kline minutes")
            klines[spec["symbol"]] = {int(r[0]): r for r in data}
            continue
        records, gaps = load_trades(spec)
        all_trades[(spec["symbol"], spec["date"])] = records
        input_checks.append({"file": spec["local_file"], "aggregate_records": len(records),
                             "aggregate_id_gaps": gaps, "timestamps_within_source_day": True,
                             "ids_and_timestamps_monotonic": True,
                             "underlying_trade_ranges_nonoverlapping": True})
        daily_rows.append({"symbol": spec["symbol"], "date": spec["date"], **summarize(records)})
        bins = collections.defaultdict(list)
        for record in records:
            bins[record["timestamp_us"] // 60_000_000 * 60_000_000].append(record)
        for minute, group in sorted(bins.items()):
            minute_rows.append({"symbol": spec["symbol"], "minute_utc": iso(minute),
                                "minute_us": minute, **summarize(group)})

    phases = [("pre_break", 21, 0, 21, 20), ("first_break", 21, 20, 21, 36),
              ("announced_window", 21, 36, 22, 16), ("after_window", 22, 16, 23, 0)]
    phase_rows = []
    threshold_rows = []
    baseline_rows = []
    extremes = {}
    for symbol in ["USDEUSDT", "USDEUSDC"]:
        records = all_trades[(symbol, EVENT)]
        total = summarize(records)
        for label, h1, m1, h2, m2 in phases:
            start, end = epoch(EVENT, h1, m1), epoch(EVENT, h2, m2)
            phase_rows.append({"symbol": symbol, "phase": label, "start_utc": iso(start),
                               "end_utc_exclusive": iso(end), **summarize(window(records, start, end))})
        for threshold in [0.99, 0.98, 0.95, 0.9, 0.8, 0.7, 0.66, 0.651]:
            subset = [r for r in records if r["price"] < threshold]
            stats = summarize(subset)
            threshold_rows.append({"symbol": symbol, "price_strictly_below": threshold,
                                   "first_utc": iso(subset[0]["timestamp_us"]) if subset else "",
                                   "last_utc": iso(subset[-1]["timestamp_us"]) if subset else "",
                                   "daily_base_volume_share": stats["base_volume"] / total["base_volume"],
                                   "daily_quote_notional_share": stats["quote_notional"] / total["quote_notional"],
                                   **stats})
        low = min(r["price"] for r in records)
        at_low = [r for r in records if r["price"] == low]
        extremes[symbol] = {"minimum_price": low, "first_minimum_utc": iso(at_low[0]["timestamp_us"]),
                            "last_minimum_utc": iso(at_low[-1]["timestamp_us"]),
                            "minimum_price_trades": summarize(at_low),
                            "minimum_price_daily_quote_share": summarize(at_low)["quote_notional"] / total["quote_notional"]}
        for (pair, day), trades in all_trades.items():
            if pair == symbol:
                baseline_rows.append({"symbol": pair, "date": day,
                                      "window": "21:00:00 <= UTC < 23:00:00",
                                      **summarize(window(trades, epoch(day, 21), epoch(day, 23)))})

    primary = all_trades[("USDEUSDT", EVENT)]
    event_minutes = {r["minute_us"]: r for r in minute_rows
                     if r["symbol"] == "USDEUSDT" and r["minute_utc"].startswith(EVENT)}
    # A second, independently published aggregation must agree with the trade reconstruction.
    max_volume_error = max_quote_error = 0.0
    for symbol in ["USDEUSDT", "USDEUSDC"]:
        reconstructed = {r["minute_us"]: r for r in minute_rows
                         if r["symbol"] == symbol and r["minute_utc"].startswith(EVENT)}
        for t, row in klines[symbol].items():
            measured = reconstructed.get(t)
            volume = measured["base_volume"] if measured else 0
            notional = measured["quote_notional"] if measured else 0
            max_volume_error = max(max_volume_error, abs(volume - float(row[5])))
            max_quote_error = max(max_quote_error, abs(notional - float(row[7])))
            if not math.isclose(volume, float(row[5]), rel_tol=1e-10, abs_tol=1e-5):
                raise ValueError(f"{symbol} trade/kline volume mismatch at {iso(t)}")
            if not math.isclose(notional, float(row[7]), rel_tol=1e-10, abs_tol=1e-4):
                raise ValueError(f"{symbol} trade/kline quote notional mismatch at {iso(t)}")
            if (measured["underlying_trades"] if measured else 0) != int(row[8]):
                raise ValueError(f"{symbol} trade/kline underlying count mismatch at {iso(t)}")
            if measured:
                for field, index in [("open", 1), ("high", 2), ("low", 3), ("close", 4)]:
                    if measured[field] != float(row[index]):
                        raise ValueError(f"{symbol} trade/kline {field} mismatch at {iso(t)}")
                buy_quantity = volume * (1 - measured["taker_sell_base_share"])
                buy_notional = notional * (1 - measured["taker_sell_quote_share"])
                if not math.isclose(buy_quantity, float(row[9]), rel_tol=1e-10, abs_tol=1e-5):
                    raise ValueError(f"{symbol} taker-buy quantity mismatch at {iso(t)}")
                if not math.isclose(buy_notional, float(row[10]), rel_tol=1e-10, abs_tol=1e-4):
                    raise ValueError(f"{symbol} taker-buy notional mismatch at {iso(t)}")

    exploratory = summarize(window(primary, epoch(EVENT, 21, 44), epoch(EVENT, 21, 54)))
    first_vwap = event_minutes[epoch(EVENT, 21, 44)]["vwap"]
    last_vwap = event_minutes[epoch(EVENT, 21, 53)]["vwap"]
    exploratory.update(start_utc="2025-10-10T21:44:00Z", end_utc_exclusive="2025-10-10T21:54:00Z",
                       first_minute_vwap=first_vwap, last_minute_vwap=last_vwap,
                       minute_vwap_change=last_vwap / first_vwap - 1,
                       selection="Exploratory interval selected after the initial price inspection; not a pre-registered test")
    control_rows = []
    for symbol, rows in klines.items():
        if symbol in ["USDCUSDT", "BTCUSDT"]:
            for t, row in rows.items():
                control_rows.append({"symbol": symbol, "minute_utc": iso(t), "minute_us": t,
                                     "open": float(row[1]), "high": float(row[2]), "low": float(row[3]),
                                     "close": float(row[4]), "base_volume": float(row[5]),
                                     "quote_notional": float(row[7]),
                                     "vwap": float(row[7]) / float(row[5]) if float(row[5]) else None})

    quote_rows = []
    usdc_minutes = {r["minute_us"]: r for r in minute_rows
                    if r["symbol"] == "USDEUSDC" and r["minute_utc"].startswith(EVENT)}
    for t in sorted(event_minutes.keys() & usdc_minutes.keys()):
        direct, indirect = event_minutes[t], usdc_minutes[t]
        control = klines["USDCUSDT"][t]
        if float(control[5]) <= 0:
            continue
        conversion = float(control[7]) / float(control[5])
        normalized = indirect["vwap"] * conversion
        quote_rows.append({"minute_utc": iso(t), "minute_us": t,
                           "usdt_pair_vwap": direct["vwap"],
                           "usdc_pair_vwap": indirect["vwap"],
                           "usdc_usdt_vwap": conversion,
                           "usdc_pair_approx_vwap_in_usdt": normalized,
                           "usdc_route_relative_gap": normalized / direct["vwap"] - 1,
                           "usdt_pair_base_volume": direct["base_volume"],
                           "usdc_pair_base_volume": indirect["base_volume"]})
    sensitivity = []
    for minimum_volume in [10_000, 100_000, 1_000_000]:
        selected = [r for r in quote_rows if epoch(EVENT, 21) <= r["minute_us"] < epoch(EVENT, 23)
                    and min(r["usdt_pair_base_volume"], r["usdc_pair_base_volume"]) >= minimum_volume]
        sensitivity.append({"minimum_base_volume_per_pair_per_minute": minimum_volume,
                            "eligible_minutes": len(selected),
                            "minutes_absolute_relative_gap_over_5_percent": sum(
                                abs(r["usdc_route_relative_gap"]) > 0.05 for r in selected),
                            "maximum_absolute_relative_gap": max(
                                (abs(r["usdc_route_relative_gap"]) for r in selected), default=None)})

    second_bins = {}
    for symbol in ["USDEUSDT", "USDEUSDC"]:
        bins = collections.defaultdict(list)
        for record in window(all_trades[(symbol, EVENT)], epoch(EVENT, 21, 46), epoch(EVENT, 21, 47)):
            bins[record["timestamp_us"] // 1_000_000 * 1_000_000].append(record)
        second_bins[symbol] = bins
    second_rows = []
    conversion_high = float(klines["USDCUSDT"][epoch(EVENT, 21, 46)][2])
    for second in sorted(second_bins["USDEUSDT"].keys() & second_bins["USDEUSDC"].keys()):
        direct = summarize(second_bins["USDEUSDT"][second])
        indirect = summarize(second_bins["USDEUSDC"][second])
        second_rows.append({"second_utc": iso(second), "usdt_pair_vwap": direct["vwap"],
                            "usdc_pair_vwap": indirect["vwap"],
                            "usdc_usdt_minute_high": conversion_high,
                            "relative_gap_using_conversion_minute_high": indirect["vwap"] * conversion_high / direct["vwap"] - 1,
                            "usdt_pair_base_volume": direct["base_volume"],
                            "usdc_pair_base_volume": indirect["base_volume"]})
    second_sensitivity = []
    for minimum_volume in [1_000, 10_000]:
        selected = [r for r in second_rows if min(r["usdt_pair_base_volume"], r["usdc_pair_base_volume"]) >= minimum_volume]
        second_sensitivity.append({"minimum_base_volume_per_pair_per_second": minimum_volume,
                                   "eligible_seconds": len(selected),
                                   "seconds_usdc_route_lower_by_over_5_percent": sum(
                                       r["relative_gap_using_conversion_minute_high"] < -0.05 for r in selected)})

    write_csv("minute_metrics.csv", minute_rows)
    write_csv("daily_summary.csv", daily_rows)
    write_csv("phase_summary.csv", phase_rows)
    write_csv("threshold_summary.csv", threshold_rows)
    write_csv("matched_clock_windows.csv", baseline_rows)
    write_csv("control_minutes.csv", control_rows)
    write_csv("quote_comparison.csv", quote_rows)
    write_csv("quote_gap_sensitivity.csv", sensitivity)
    write_csv("same_second_comparison_2146.csv", second_rows)
    deepest = [{"timestamp_utc": iso(r["timestamp_us"]), **r}
               for r in primary if r["price"] <= 0.66]
    write_csv("deepest_executions.csv", deepest)
    result = {"event_date": EVENT, "archives": len(manifest["archives"]),
              "aggregate_records_analyzed": sum(len(r) for r in all_trades.values()),
              "input_checks": input_checks,
              "kline_crosscheck": {"minutes_per_pair": 1440, "pairs": ["USDEUSDT", "USDEUSDC"],
                                    "OHLC_and_underlying_trade_counts_match": True,
                                    "taker_buy_base_and_quote_volumes_match": True,
                                    "max_absolute_base_volume_difference": max_volume_error,
                                    "max_absolute_quote_notional_difference": max_quote_error},
              "event_daily": [r for r in daily_rows if r["date"] == EVENT],
              "extremes": extremes, "exploratory_recovery_window": exploratory,
              "quote_gap_sensitivity": sensitivity,
              "same_second_sensitivity_at_2146": second_sensitivity,
              "quote_comparison_at_2146": next(r for r in quote_rows if r["minute_us"] == epoch(EVENT, 21, 46)),
              "baseline_median_quote_notional_21_to_23": {
                  s: statistics.median(r["quote_notional"] for r in baseline_rows
                                       if r["symbol"] == s and r["date"] < EVENT)
                  for s in ["USDEUSDT", "USDEUSDC"]},
              "missing_minutes_policy": "No interpolation or forward-fill; no-trade minutes are absent from trade metrics",
              "scope": "One venue, two USDE spot pairs and two Binance control pairs; no independent Bybit data"}
    (ROOT / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "input_checks"}, indent=2))


if __name__ == "__main__":
    main()
