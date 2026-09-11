#!/usr/bin/env python3
"""Download fixed public Binance archives and verify their published SHA-256 sums."""

import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
BASE = "https://data.binance.vision/data/spot/daily"
DATES = [dt.date(2025, 10, day).isoformat() for day in range(3, 12)]


def specifications():
    specs = []
    for symbol in ["USDEUSDT", "USDEUSDC"]:
        for date in DATES:
            filename = f"{symbol}-aggTrades-{date}.zip"
            specs.append({"symbol": symbol, "date": date, "kind": "aggTrades",
                          "url": f"{BASE}/aggTrades/{symbol}/{filename}",
                          "local_file": f"binance-{symbol}-{date}.zip"})
    for symbol in ["USDCUSDT", "BTCUSDT", "USDEUSDT", "USDEUSDC"]:
        date = "2025-10-10"
        filename = f"{symbol}-1m-{date}.zip"
        specs.append({"symbol": symbol, "date": date, "kind": "1m-klines",
                      "url": f"{BASE}/klines/{symbol}/1m/{filename}",
                      "local_file": f"binance-{symbol}-1m-{date}.zip"})
    return specs


def download(url, destination):
    temporary = destination.with_name(destination.name + ".part")
    result = subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--location",
         "--connect-timeout", "10", "--max-time", "30", url, "--output", str(temporary)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Download failed for {url}: {result.stderr.strip()}")
    temporary.replace(destination)


def fetch(spec):
    spec = dict(spec)
    destination = RAW / spec["local_file"]
    checksum = destination.with_name(destination.name + ".CHECKSUM")
    if not destination.exists():
        download(spec["url"], destination)
    if not checksum.exists():
        download(spec["url"] + ".CHECKSUM", checksum)
    expected = checksum.read_text().split()[0]
    actual = hashlib.sha256(destination.read_bytes()).hexdigest()
    if len(expected) != 64 or expected != actual:
        raise ValueError(f"Published checksum mismatch: {destination}")
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        if len(names) != 1 or not names[0].endswith(".csv"):
            raise ValueError(f"Expected exactly one CSV member: {destination}")
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ValueError(f"ZIP CRC failure: {destination}: {bad_member}")
        info = archive.getinfo(names[0])
    spec.update(sha256=actual, published_sha256=expected,
                published_checksum_verified=True, bytes=destination.stat().st_size,
                uncompressed_bytes=info.file_size, csv_member=info.filename)
    return spec


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, specifications()))
    manifest = {"download_checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "source": "Binance public market-data archives",
                "source_documentation": "https://github.com/binance/binance-public-data",
                "archives": results}
    (ROOT / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"archives": len(results), "published_checksums_verified": len(results),
                      "compressed_bytes": sum(r["bytes"] for r in results)}))


if __name__ == "__main__":
    main()
