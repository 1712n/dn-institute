"""Reproduce the MCRT mark and returns with the Python standard library.

Run this file directly for the offline calculation. For an additional source
check, pass --archive MCRTUSDT-2026-05.csv.gz, downloaded from:
https://public.bybit.com/spot/MCRTUSDT/MCRTUSDT-2026-05.csv.gz
"""

import argparse
import csv
import gzip
import hashlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from statistics import mean, median

DATA = Path(__file__).resolve().parent / "data" / "mcrt"
ARCHIVE_SHA256 = "89459c5d4f12a3e7059231e67cfadbf531980c4cc8e95162b0d071d5b358a232"
DAY = datetime(2026, 5, 27, tzinfo=timezone.utc)
START_MS = int(DAY.timestamp()) * 1000
END_MS = int((DAY + timedelta(days=1)).timestamp()) * 1000
DAY_FIELDS = ["trade_id", "timestamp_ms", "price", "volume", "side"]


def check_archive(path, day_rows):
    with path.open("rb") as archive:
        digest = hashlib.sha256(archive.read()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise ValueError("The compressed archive SHA-256 differs from the published source.")
    with gzip.open(path, "rt", encoding="ascii", newline="") as source:
        records = csv.reader(source)
        # The archive header omits an extra trailing field present in each row.
        if next(records) != ["id", "timestamp", "price", "volume", "side"]:
            raise ValueError("Unexpected Bybit archive header.")
        selected = [row[:5] for row in records if START_MS <= int(row[1]) < END_MS]
    if selected != [[row[key] for key in DAY_FIELDS] for row in day_rows]:
        raise ValueError("The committed day tape differs from the source archive.")
    print(f"Source verified: {len(selected):,} trades; SHA-256 {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="verify the day tape against the Bybit monthly archive")
    args = parser.parse_args()
    with (DATA / "trades_2026-05-27.csv").open(encoding="ascii", newline="") as stream:
        day_rows = list(csv.DictReader(stream))
    if not all(START_MS <= int(row["timestamp_ms"]) < END_MS for row in day_rows):
        raise ValueError("The day tape contains a trade outside 27 May UTC.")
    if args.archive:
        check_archive(args.archive, day_rows)
    mark = median(Decimal(row["price"]) for row in day_rows)

    with (DATA / "late_buyers.csv").open(encoding="ascii", newline="") as stream:
        fills = list(csv.DictReader(stream))
    prices = [Decimal(row["price"]) for row in fills]
    tokens = sum(Decimal(row["volume"]) for row in fills)
    cost = sum(Decimal(row["notional"]) for row in fills)
    mean_return = mean(mark / price - 1 for price in prices)
    pooled_return = mark * tokens / cost - 1
    print(f"27 May UTC: {len(day_rows):,} trades, median {mark:f} USDT/MCRT")
    print(f"{len(fills)} buy executions: {tokens:,.2f} MCRT, {cost:,.2f} USDT")
    print(f"Mean execution price: {mean(prices):.10f}; VWAP: {cost / tokens:.10f} USDT/MCRT")
    print(f"Mean execution return: {mean_return:.5%}; pooled return: {pooled_return:.5%}")


if __name__ == "__main__":
    main()
