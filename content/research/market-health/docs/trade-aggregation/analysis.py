#!/usr/bin/env python3
"""Reproducible, offline analysis of official ADAUSDT Spot trade archives."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, getcontext
import hashlib
import io
import json
from pathlib import Path
import zipfile


getcontext().prec = 50

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
TRADES_ARCHIVE = RAW / "ADAUSDT-trades-2026-09-10.zip"
AGG_ARCHIVE = RAW / "ADAUSDT-aggTrades-2026-09-10.zip"
TRADES_CHECKSUM = RAW / "ADAUSDT-trades-2026-09-10.zip.CHECKSUM"
AGG_CHECKSUM = RAW / "ADAUSDT-aggTrades-2026-09-10.zip.CHECKSUM"
METRICS = ROOT / "metrics.json"
PROVENANCE = ROOT / "provenance.json"
FIRST_DIGIT_CHART = ROOT / "first_digit_distribution.png"
ROUND_RATE_CHART = ROOT / "round_number_rates.png"
REQUIREMENTS = ROOT / "requirements.txt"
DAY_START_US = 1788998400000000
DAY_END_US = 1789084800000000

TRADES_URL = "https://data.binance.vision/data/spot/daily/trades/ADAUSDT/ADAUSDT-trades-2026-09-10.zip"
AGG_URL = "https://data.binance.vision/data/spot/daily/aggTrades/ADAUSDT/ADAUSDT-aggTrades-2026-09-10.zip"
README_URL = "https://raw.githubusercontent.com/binance/binance-public-data/master/README.md"


class DataError(ValueError):
    pass


@dataclass(frozen=True)
class Trade:
    trade_id: int
    price: Decimal
    quantity: Decimal
    quote_quantity: Decimal
    timestamp: int
    buyer_is_maker: bool
    best_match: bool


@dataclass(frozen=True)
class AggregateTrade:
    aggregate_id: int
    price: Decimal
    quantity: Decimal
    first_trade_id: int
    last_trade_id: int
    timestamp: int
    buyer_is_maker: bool
    best_match: bool


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_expected(path: Path) -> str:
    try:
        fields = path.read_text(encoding="utf-8").strip().split()
    except OSError as error:
        raise DataError(f"unreadable checksum sidecar: {path.name}") from error
    if len(fields) != 2 or len(fields[0]) != 64 or any(char not in "0123456789abcdef" for char in fields[0]):
        raise DataError(f"malformed checksum sidecar: {path.name}")
    return fields[0]


def verify_archive(archive: Path, sidecar: Path, expected: str) -> dict:
    actual = sha256_path(archive)
    sidecar_hash = checksum_expected(sidecar)
    if actual != expected or sidecar_hash != expected:
        raise DataError(f"checksum mismatch for {archive.name}")
    return {"archive": archive.name, "sha256": actual, "sidecar": sidecar.name, "verified": True}


def decimal_field(value: str, label: str, row_number: int) -> Decimal:
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError) as error:
        raise DataError(f"invalid {label} at CSV row {row_number}") from error
    if not number.is_finite() or number <= 0:
        raise DataError(f"non-positive or non-finite {label} at CSV row {row_number}")
    return number


def integer_field(value: str, label: str, row_number: int) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise DataError(f"invalid {label} at CSV row {row_number}") from error
    if number < 0:
        raise DataError(f"negative {label} at CSV row {row_number}")
    return number


def bool_field(value: str, label: str, row_number: int) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise DataError(f"invalid {label} at CSV row {row_number}")


def archive_rows(archive: Path, expected_columns: int):
    try:
        with zipfile.ZipFile(archive) as zipped:
            names = zipped.namelist()
            if len(names) != 1 or not names[0].endswith(".csv"):
                raise DataError(f"archive schema is not one CSV: {archive.name}")
            with zipped.open(names[0]) as binary, io.TextIOWrapper(binary, encoding="utf-8", newline="") as text:
                reader = csv.reader(text, strict=True)
                for row_number, row in enumerate(reader, start=1):
                    if len(row) != expected_columns:
                        raise DataError(f"unexpected field count at {archive.name} CSV row {row_number}")
                    yield row_number, row
    except (OSError, zipfile.BadZipFile, csv.Error, UnicodeError) as error:
        if isinstance(error, DataError):
            raise
        raise DataError(f"unreadable CSV archive: {archive.name}") from error


def load_trades(archive: Path) -> list[Trade]:
    rows = []
    previous_id = None
    for line, row in archive_rows(archive, 7):
        trade = Trade(
            integer_field(row[0], "trade id", line), decimal_field(row[1], "price", line),
            decimal_field(row[2], "quantity", line), decimal_field(row[3], "quote quantity", line),
            integer_field(row[4], "timestamp", line), bool_field(row[5], "buyer maker flag", line),
            bool_field(row[6], "best-match flag", line),
        )
        if previous_id is not None and trade.trade_id <= previous_id:
            raise DataError(f"trade IDs are not strictly increasing at CSV row {line}")
        rows.append(trade)
        previous_id = trade.trade_id
    if not rows:
        raise DataError("trades archive is empty")
    return rows


def load_aggregates(archive: Path) -> list[AggregateTrade]:
    rows = []
    previous_id = None
    for line, row in archive_rows(archive, 8):
        aggregate = AggregateTrade(
            integer_field(row[0], "aggregate trade id", line), decimal_field(row[1], "price", line),
            decimal_field(row[2], "quantity", line), integer_field(row[3], "first trade id", line),
            integer_field(row[4], "last trade id", line), integer_field(row[5], "timestamp", line),
            bool_field(row[6], "buyer maker flag", line), bool_field(row[7], "best-match flag", line),
        )
        if aggregate.last_trade_id < aggregate.first_trade_id:
            raise DataError(f"aggregate range is reversed at CSV row {line}")
        if previous_id is not None and aggregate.aggregate_id <= previous_id:
            raise DataError(f"aggregate IDs are not strictly increasing at CSV row {line}")
        rows.append(aggregate)
        previous_id = aggregate.aggregate_id
    if not rows:
        raise DataError("aggregate archive is empty")
    return rows


def first_digit(quantity: Decimal) -> str:
    digits = quantity.normalize().as_tuple().digits
    if not digits:
        raise DataError("zero quantity passed to first-digit calculation")
    return str(digits[0])


def decimal_rate(count: int, total: int) -> str:
    if total <= 0:
        raise DataError("cannot calculate a rate from an empty sample")
    return format(Decimal(count) / Decimal(total), "f")


def distribution(quantities: list[Decimal]) -> dict:
    counts = {str(digit): 0 for digit in range(1, 10)}
    for quantity in quantities:
        counts[first_digit(quantity)] += 1
    total = len(quantities)
    return {digit: {"count": counts[digit], "rate": decimal_rate(counts[digit], total)} for digit in counts}


def round_rate(quantities: list[Decimal]) -> dict:
    whole = sum(quantity == quantity.to_integral_value() for quantity in quantities)
    total = len(quantities)
    return {"definition": "quantity is exactly equal to its integral Decimal value", "count": whole,
            "sample_count": total, "rate": decimal_rate(whole, total)}


def reconciliation(raw: list[Trade], aggregates: list[AggregateTrade]) -> dict:
    index = {trade.trade_id: position for position, trade in enumerate(raw)}
    if len(index) != len(raw):
        raise DataError("duplicate raw trade ID")
    failures = {key: 0 for key in (
        "missing_or_noncontiguous_id_range", "overlapping_or_uncovered_raw_ranges", "quantity_mismatch",
        "price_mismatch", "buyer_maker_mismatch", "best_match_mismatch", "timestamp_outside_raw_range",
    )}
    first_failure = {}
    expected_start = 0
    timestamp_equals_last = 0
    for aggregate in aggregates:
        start, end = index.get(aggregate.first_trade_id), index.get(aggregate.last_trade_id)
        if start is None or end is None or start > end:
            failures["missing_or_noncontiguous_id_range"] += 1
            first_failure.setdefault("missing_or_noncontiguous_id_range", aggregate.aggregate_id)
            continue
        segment = raw[start:end + 1]
        ids_contiguous = len(segment) == aggregate.last_trade_id - aggregate.first_trade_id + 1 and all(
            trade.trade_id == aggregate.first_trade_id + offset for offset, trade in enumerate(segment)
        )
        if not ids_contiguous:
            failures["missing_or_noncontiguous_id_range"] += 1
            first_failure.setdefault("missing_or_noncontiguous_id_range", aggregate.aggregate_id)
        if start != expected_start:
            failures["overlapping_or_uncovered_raw_ranges"] += 1
            first_failure.setdefault("overlapping_or_uncovered_raw_ranges", aggregate.aggregate_id)
        expected_start = max(expected_start, end + 1)
        if sum((trade.quantity for trade in segment), Decimal("0")) != aggregate.quantity:
            failures["quantity_mismatch"] += 1
            first_failure.setdefault("quantity_mismatch", aggregate.aggregate_id)
        if any(trade.price != aggregate.price for trade in segment):
            failures["price_mismatch"] += 1
            first_failure.setdefault("price_mismatch", aggregate.aggregate_id)
        if any(trade.buyer_is_maker != aggregate.buyer_is_maker for trade in segment):
            failures["buyer_maker_mismatch"] += 1
            first_failure.setdefault("buyer_maker_mismatch", aggregate.aggregate_id)
        if any(trade.best_match != aggregate.best_match for trade in segment):
            failures["best_match_mismatch"] += 1
            first_failure.setdefault("best_match_mismatch", aggregate.aggregate_id)
        first_time, last_time = min(trade.timestamp for trade in segment), max(trade.timestamp for trade in segment)
        if not first_time <= aggregate.timestamp <= last_time:
            failures["timestamp_outside_raw_range"] += 1
            first_failure.setdefault("timestamp_outside_raw_range", aggregate.aggregate_id)
        if aggregate.timestamp == segment[-1].timestamp:
            timestamp_equals_last += 1
    if expected_start != len(raw):
        failures["overlapping_or_uncovered_raw_ranges"] += 1
        first_failure.setdefault("overlapping_or_uncovered_raw_ranges", "tail")
    raw_total = sum((trade.quantity for trade in raw), Decimal("0"))
    aggregate_total = sum((aggregate.quantity for aggregate in aggregates), Decimal("0"))
    total_difference = aggregate_total - raw_total
    if total_difference != 0:
        failures["total_base_quantity_mismatch"] = 1
        first_failure.setdefault("total_base_quantity_mismatch", "all rows")
    else:
        failures["total_base_quantity_mismatch"] = 0
    return {
        "aggregate_rows_checked": len(aggregates), "raw_rows_checked": len(raw), "failure_counts": failures,
        "first_failing_aggregate_id": first_failure, "all_checks_passed": not any(failures.values()),
        "aggregate_timestamps_equal_last_raw_timestamp_count": timestamp_equals_last,
        "aggregate_timestamp_rule_tested": "aggregate timestamp lies within inclusive min/max raw timestamp range",
        "total_base_quantity": {"raw_trades": format(raw_total, "f"), "aggregate_trades": format(aggregate_total, "f"),
                                "aggregate_minus_raw": format(total_difference, "f"), "matches_exactly": total_difference == 0},
    }


def timestamp_info(raw: list[Trade], aggregates: list[AggregateTrade]) -> dict:
    values = [trade.timestamp for trade in raw] + [aggregate.timestamp for aggregate in aggregates]
    digits = sorted({len(str(value)) for value in values})
    detected = "microseconds" if all(10**15 <= value < 10**16 for value in values) else "milliseconds_or_other"
    return {"official_schema_note": "Binance public-data README states Spot timestamps from 2025-01-01 onward are microseconds.",
            "observed_decimal_digit_lengths": digits, "detected_unit": detected,
            "minimum_timestamp": min(values), "maximum_timestamp": max(values),
            "all_timestamps_within_requested_utc_day": all(DAY_START_US <= value < DAY_END_US for value in values),
            "requested_utc_day_bounds_microseconds": [DAY_START_US, DAY_END_US]}


def decimal_delta(agg_rate: str, raw_rate: str) -> str:
    return format(Decimal(agg_rate) - Decimal(raw_rate), "f")


def benford_probability(digit: int) -> Decimal:
    if digit not in range(1, 10):
        raise DataError("Benford digit must be 1 through 9")
    return (Decimal(1) + Decimal(1) / Decimal(digit)).log10()


def benford_diagnostics(source_distribution: dict) -> dict:
    expected = {str(digit): benford_probability(digit) for digit in range(1, 10)}
    observed = {digit: Decimal(source_distribution[digit]["rate"]) for digit in source_distribution}
    absolute_differences = [abs(observed[digit] - expected[digit]) for digit in observed]
    observed_cdf = Decimal(0)
    expected_cdf = Decimal(0)
    max_cdf_distance = Decimal(0)
    for digit in observed:
        observed_cdf += observed[digit]
        expected_cdf += expected[digit]
        max_cdf_distance = max(max_cdf_distance, abs(observed_cdf - expected_cdf))
    return {
        "benford_expected_rates": {digit: format(expected[digit], "f") for digit in expected},
        "mean_absolute_deviation": format(sum(absolute_differences, Decimal(0)) / Decimal(9), "f"),
        "maximum_cdf_distance": format(max_cdf_distance, "f"),
        "scope_note": "Descriptive distance measures only. No p-values or independence claims are made.",
    }


def total_variation_distance(left: dict, right: dict) -> str:
    return format(sum((abs(Decimal(left[digit]["rate"]) - Decimal(right[digit]["rate"])) for digit in left), Decimal(0)) / 2, "f")


def quantity_24_7(raw: list[Trade], aggregates: list[AggregateTrade]) -> dict:
    target = Decimal("24.7")

    def source_summary(rows):
        count = sum(row.quantity == target for row in rows)
        total = sum((row.quantity for row in rows), Decimal(0))
        return {"row_count": count, "row_prevalence_rate": decimal_rate(count, len(rows)),
                "base_quantity": format(target * count, "f"), "total_base_quantity": format(total, "f"),
                "base_quantity_volume_share": format((target * count) / total, "f")}

    return {"quantity": "24.7", "raw_trades": source_summary(raw), "aggregate_trades": source_summary(aggregates)}


def utc_hour(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp // 1_000_000, timezone.utc).strftime("%H")


def hourly_leading_digit_two(raw: list[Trade], aggregates: list[AggregateTrade]) -> dict:
    raw_hours = {f"{hour:02d}": [] for hour in range(24)}
    aggregate_hours = {f"{hour:02d}": [] for hour in range(24)}
    for trade in raw:
        raw_hours[utc_hour(trade.timestamp)].append(trade.quantity)
    raw_index = {trade.trade_id: position for position, trade in enumerate(raw)}
    crossing_ids = []
    for aggregate in aggregates:
        start, end = raw_index[aggregate.first_trade_id], raw_index[aggregate.last_trade_id]
        segment = raw[start:end + 1]
        covered_hours = {utc_hour(trade.timestamp) for trade in segment}
        if len(covered_hours) != 1:
            crossing_ids.append(aggregate.aggregate_id)
            continue
        aggregate_hours[covered_hours.pop()].append(aggregate.quantity)

    def hour_summary(quantities):
        count = len(quantities)
        leading_two = sum(first_digit(quantity) == "2" for quantity in quantities)
        return {"row_count": count, "leading_digit_2_count": leading_two,
                "leading_digit_2_rate": None if count == 0 else decimal_rate(leading_two, count)}

    hours = {}
    for hour in raw_hours:
        raw_summary, aggregate_summary = hour_summary(raw_hours[hour]), hour_summary(aggregate_hours[hour])
        raw_rate, aggregate_rate = raw_summary["leading_digit_2_rate"], aggregate_summary["leading_digit_2_rate"]
        hours[hour] = {"raw_trades": raw_summary, "aggregate_trades": aggregate_summary,
                       "aggregate_minus_raw_rate": None if raw_rate is None or aggregate_rate is None else decimal_delta(aggregate_rate, raw_rate)}
    return {
        "definition": "First significant base-quantity digit equals 2. Rates use row counts, not volume.",
        "aggregate_ranges_crossing_utc_hour_boundary": len(crossing_ids),
        "crossing_aggregate_ids_sample": crossing_ids[:10],
        "crossing_range_treatment": "Excluded from aggregate hourly rates; no aggregate is assigned to a single hour when its raw range crosses a UTC-hour boundary.",
        "hours_utc": hours,
    }


def metrics(raw: list[Trade], aggregates: list[AggregateTrade]) -> dict:
    raw_quantities = [trade.quantity for trade in raw]
    aggregate_quantities = [aggregate.quantity for aggregate in aggregates]
    raw_digits, aggregate_digits = distribution(raw_quantities), distribution(aggregate_quantities)
    raw_round, aggregate_round = round_rate(raw_quantities), round_rate(aggregate_quantities)
    reconcile = reconciliation(raw, aggregates)
    return {
        "dataset": {"symbol": "ADAUSDT", "market": "Spot", "date_utc": "2026-09-10"},
        "timestamp": timestamp_info(raw, aggregates),
        "sample_counts": {"raw_trades": len(raw), "aggregate_trades": len(aggregates),
                          "raw_trades_per_aggregate_trade": decimal_rate(len(raw), len(aggregates))},
        "first_digit_base_quantity_distribution": {"raw_trades": raw_digits, "aggregate_trades": aggregate_digits,
            "aggregate_minus_raw_rate": {digit: decimal_delta(aggregate_digits[digit]["rate"], raw_digits[digit]["rate"])
                                          for digit in raw_digits},
            "raw_vs_aggregate_total_variation_distance": total_variation_distance(raw_digits, aggregate_digits),
            "benford_descriptive_diagnostics": {"raw_trades": benford_diagnostics(raw_digits),
                                                  "aggregate_trades": benford_diagnostics(aggregate_digits)}},
        "exact_round_number_base_quantity_rate": {"raw_trades": raw_round, "aggregate_trades": aggregate_round,
            "aggregate_minus_raw_rate": decimal_delta(aggregate_round["rate"], raw_round["rate"])},
        "quantity_24_7": quantity_24_7(raw, aggregates),
        "hourly_leading_digit_2": hourly_leading_digit_two(raw, aggregates),
        "reconciliation": reconcile,
        "methods": {"quantity_precision": "Python Decimal parsed directly from archive text; no float arithmetic.",
                    "first_digit": "First significant decimal digit of positive base quantity after Decimal normalization.",
                    "deduplication": "None. Every archive row is counted once in its own source file."},
        "interpretation_limit": "This descriptive archive comparison does not infer intent, misconduct, or fraud.",
    }


def charts(result: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plot
    from matplotlib.ticker import PercentFormatter

    digits = result["first_digit_base_quantity_distribution"]
    labels = list(digits["raw_trades"])
    positions = list(range(len(labels)))
    raw_values = [float(Decimal(digits["raw_trades"][label]["rate"])) for label in labels]
    aggregate_values = [float(Decimal(digits["aggregate_trades"][label]["rate"])) for label in labels]
    benford = [float(Decimal(digits["benford_descriptive_diagnostics"]["raw_trades"]["benford_expected_rates"][label])) for label in labels]
    figure, axis = plot.subplots(figsize=(12, 7), constrained_layout=True)
    width = 0.28
    axis.bar([value - width / 2 for value in positions], raw_values, width, label="Raw trades", color="#2563eb")
    axis.bar([value + width / 2 for value in positions], aggregate_values, width, label="Aggregate trades", color="#dc2626")
    axis.plot(positions, benford, color="#111827", marker="o", linestyle="--", label="Benford reference")
    axis.set_xticks(positions, labels)
    axis.yaxis.set_major_formatter(PercentFormatter(1))
    axis.set_ylabel("Share of rows")
    axis.set_xlabel("First significant base-quantity digit")
    axis.set_title("ADAUSDT Spot, 2026-09-10: first-digit distribution")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(ncol=3, frameon=False)
    axis.text(0.5, -0.18, "Row-count shares, not volume. Benford line is descriptive only.", transform=axis.transAxes,
              ha="center", va="top", fontsize=10)
    figure.savefig(FIRST_DIGIT_CHART, dpi=180)
    plot.close(figure)

    round_rates = result["exact_round_number_base_quantity_rate"]
    values = [float(Decimal(round_rates["raw_trades"]["rate"])), float(Decimal(round_rates["aggregate_trades"]["rate"]))]
    figure, axis = plot.subplots(figsize=(9, 6), constrained_layout=True)
    bars = axis.bar(["Raw trades", "Aggregate trades"], values, color=["#2563eb", "#dc2626"])
    axis.yaxis.set_major_formatter(PercentFormatter(1))
    axis.set_ylim(0, max(values) * 1.25)
    axis.set_ylabel("Share of rows")
    axis.set_title("ADAUSDT Spot, 2026-09-10: exact whole-unit quantity rate")
    axis.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values):
        axis.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2%}", ha="center", va="bottom")
    axis.text(0.5, -0.15, "A whole-unit quantity equals its integral Decimal value. Row counts, not volume.",
              transform=axis.transAxes, ha="center", va="top", fontsize=10)
    figure.savefig(ROUND_RATE_CHART, dpi=180)
    plot.close(figure)


def atomic_json(path: Path, value: dict):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    expected = {
        TRADES_ARCHIVE: "5a0e9637b65bd62ab3c5ea2af10b4ed5ab5526b070b1cbd50cb97abe4b02fa61",
        AGG_ARCHIVE: "da9d4a49f0508e3b9b4e77b6464986c04af16d9e62581cb59442fae7a317d245",
    }
    verification = [verify_archive(TRADES_ARCHIVE, TRADES_CHECKSUM, expected[TRADES_ARCHIVE]),
                    verify_archive(AGG_ARCHIVE, AGG_CHECKSUM, expected[AGG_ARCHIVE])]
    raw, aggregates = load_trades(TRADES_ARCHIVE), load_aggregates(AGG_ARCHIVE)
    result = metrics(raw, aggregates)
    if not result["reconciliation"]["all_checks_passed"]:
        raise DataError("aggregate reconciliation failed")
    if result["timestamp"]["detected_unit"] != "microseconds" or not result["timestamp"]["all_timestamps_within_requested_utc_day"]:
        raise DataError("timestamps are outside the expected microsecond 2026-09-10 UTC range")
    atomic_json(METRICS, result)
    charts(result)
    atomic_json(PROVENANCE, {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "official_sources": {"trades_archive": TRADES_URL, "aggregate_archive": AGG_URL,
                             "public_data_readme_schema": README_URL},
        "archive_verification": verification,
        "schema_reference": {
            "url": README_URL,
            "reference_readme_sha256_observed_2026_09_13": "085ab91377aa9325d44f4c7ad27cce4ab381e158403e1d7df2bad39d1a66f7c6",
            "raw_trade_columns": ["trade_id", "price", "base_quantity", "quote_quantity", "timestamp", "buyer_is_maker", "best_match"],
            "aggregate_columns": ["aggregate_id", "price", "base_quantity", "first_trade_id", "last_trade_id", "timestamp", "buyer_is_maker", "best_match"],
            "note": "Reference document is cited, not bundled; offline execution verifies the two pinned data archives."
        },
        "analysis_script_sha256": sha256_path(Path(__file__)),
        "requirements": {"path": REQUIREMENTS.name, "sha256": sha256_path(REQUIREMENTS),
                         "pinned": [line for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines() if line]},
        "outputs": [METRICS.name, FIRST_DIGIT_CHART.name, ROUND_RATE_CHART.name],
    })
    print(json.dumps({"ok": True, "raw_trades": len(raw), "aggregate_trades": len(aggregates),
                      "reconciliation_passed": result["reconciliation"]["all_checks_passed"]}))


if __name__ == "__main__":
    main()
