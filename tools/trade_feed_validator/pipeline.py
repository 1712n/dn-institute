"""Validate trade feed CSVs and publish clean trades, dead letters and a report.

Replaces the original `for event in feed: insert(parse(event))` loop. Every
input row lands in exactly one output:

  clean_trades.csv    accepted trades, normalised, sorted by chain order
  dead_letter.jsonl   rows that need repair, with reason codes and the raw row
  duplicates.jsonl    redeliveries that were dropped, with the canonical event
  report.json         counts, reason codes and volume before/after validation

Exit codes: 0 success, 1 quality gate failed, 2 unreadable input or bad usage.
"""

from __future__ import annotations

import argparse
import csv
import decimal
import io
import json
import os
import sys
import tempfile
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from validator import REQUIRED_FIELDS, Config, ConfigError, Outcome, Status, Trade, TradeFeedValidator, parse_amount

CLEAN_COLUMNS = ("event_id", "tx_hash", "block_time", "wallet", "side", "amount", "ingested_at", "log_index", "flags")
OUTPUT_FILES = ("clean_trades.csv", "dead_letter.jsonl", "duplicates.jsonl", "report.json")


class FeedError(Exception):
    """The input cannot be read as a trade feed at all."""


@dataclass(frozen=True)
class Row:
    source: str
    line: int
    raw: dict[str, str]
    # Values beyond the header; kept so a malformed row is never truncated.
    extra_values: list[str]
    malformed: bool


@dataclass(frozen=True)
class Result:
    row: Row
    outcome: Outcome


def read_feed(path: Path) -> Iterator[Row]:
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = [name.strip() for name in next(reader, [])]
            _check_header(path, header)
            for values in reader:
                if not any(value.strip() for value in values):
                    continue
                yield Row(
                    source=str(path),
                    line=reader.line_num,
                    raw=dict(zip(header, values)),
                    extra_values=values[len(header) :],
                    malformed=len(values) != len(header),
                )
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise FeedError(f"{path}: {e}") from e


def _check_header(path: Path, header: list[str]) -> None:
    if not header:
        raise FeedError(f"{path}: empty file")
    repeated = sorted({name for name in header if header.count(name) > 1})
    if repeated:
        raise FeedError(f"{path}: repeated columns {repeated}")
    missing = [name for name in REQUIRED_FIELDS if name not in header]
    if missing:
        raise FeedError(f"{path}: missing columns {missing}")


def validate(paths: Iterable[Path], config: Config) -> list[Result]:
    validator = TradeFeedValidator(config)
    results = []
    for path in paths:
        for row in read_feed(path):
            if row.malformed:
                outcome = Outcome(Status.DEAD_LETTER, ("malformed_row",))
            else:
                outcome = validator.process(row.raw)
            results.append(Result(row, outcome))
    return results


def build_report(results: list[Result], max_dead_letter_ratio: float | None) -> dict:
    by_status = {status: [r for r in results if r.outcome.status is status] for status in Status}
    dead_letter_ratio = len(by_status[Status.DEAD_LETTER]) / len(results) if results else 0.0
    passed = max_dead_letter_ratio is None or dead_letter_ratio <= max_dead_letter_ratio
    return {
        "rows": len(results),
        **{status.value: len(rows) for status, rows in by_status.items()},
        "dead_letter_ratio": round(dead_letter_ratio, 4),
        "reasons": dict(Counter(reason for r in results for reason in r.outcome.reasons)),
        "flags": dict(Counter(flag for r in results for flag in r.outcome.flags)),
        "volume": {
            # What the original insert-everything pipeline would have reported.
            "naive": _volume(results),
            "clean": _volume(by_status[Status.ACCEPTED]),
            "dead_letter": _volume(by_status[Status.DEAD_LETTER]),
        },
        "quality_gate": {"max_dead_letter_ratio": max_dead_letter_ratio, "passed": passed},
    }


def _volume(results: list[Result]) -> dict[str, str]:
    totals = {"BUY": Decimal(0), "SELL": Decimal(0)}
    # Exact sums: amounts may carry up to 78 digits (uint256).
    with decimal.localcontext() as ctx:
        ctx.prec = 200
        for r in results:
            side = (r.row.raw.get("side") or "").strip().upper()
            try:
                amount = parse_amount((r.row.raw.get("amount") or "").strip())
            except ValueError:
                continue
            if side in totals:
                totals[side] += amount
        totals["total"] = totals["BUY"] + totals["SELL"]
    return {side: _format_decimal(value) for side, value in totals.items()}


def publish(results: list[Result], report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    accepted = sorted(
        (r.outcome for r in results if r.outcome.status is Status.ACCEPTED),
        key=lambda o: _chain_order(o.trade),
    )
    files = {
        "dead_letter.jsonl": _jsonl(_rejected_record(r) for r in results if r.outcome.status is Status.DEAD_LETTER),
        "duplicates.jsonl": _jsonl(_rejected_record(r) for r in results if r.outcome.status is Status.DUPLICATE),
        "report.json": json.dumps(report, indent=2) + "\n",
    }
    if report["quality_gate"]["passed"]:
        files["clean_trades.csv"] = _clean_csv(accepted)
    else:
        # Never leave a previous run's clean output next to this run's report.
        (out_dir / "clean_trades.csv").unlink(missing_ok=True)
    for name, content in files.items():
        _write_atomic(out_dir / name, content)


def _chain_order(t: Trade) -> tuple:
    return (t.block_time, t.tx_hash, -1 if t.log_index is None else t.log_index, t.event_id)


def _clean_csv(outcomes: list[Outcome]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CLEAN_COLUMNS)
    for o in outcomes:
        t = o.trade
        writer.writerow(
            (
                t.event_id,
                t.tx_hash,
                _iso(t.block_time),
                t.wallet,
                t.side,
                _format_decimal(t.amount),
                _iso(t.ingested_at),
                "" if t.log_index is None else t.log_index,
                ";".join(o.flags),
            )
        )
    return buffer.getvalue()


def _rejected_record(r: Result) -> dict:
    record = {
        "source": r.row.source,
        "line": r.row.line,
        "event_id": r.row.raw.get("event_id"),
        "status": r.outcome.status.value,
        "reasons": list(r.outcome.reasons),
        "related_event": r.outcome.related_event,
        "raw": r.row.raw,
    }
    if r.row.extra_values:
        record["extra_values"] = r.row.extra_values
    return record


def _jsonl(records: Iterable[dict]) -> str:
    return "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)


def _write_atomic(path: Path, content: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _format_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f") if value else "0"


def _print_summary(results: list[Result], report: dict, out_dir: Path) -> None:
    print(f"{'line':>4}  {'event_id':<10} {'status':<12} detail")
    for r in results:
        o = r.outcome
        detail = ", ".join(o.reasons + o.flags)
        if o.related_event and o.related_event != r.row.raw.get("event_id"):
            detail += f" (of {o.related_event})" if o.status is Status.DUPLICATE else f" (vs {o.related_event})"
        print(f"{r.row.line:>4}  {r.row.raw.get('event_id') or '-':<10} {o.status.value:<12} {detail}".rstrip())
    volume = report["volume"]
    print(
        f"\nrows={report['rows']} accepted={report['accepted']} duplicate={report['duplicate']} "
        f"dead_letter={report['dead_letter']} (ratio {report['dead_letter_ratio']})"
    )
    for name in ("naive", "clean", "dead_letter"):
        v = volume[name]
        print(f"volume {name:<12} total={v['total']:>8} BUY={v['BUY']:>8} SELL={v['SELL']:>8}")
    gate = report["quality_gate"]
    if not gate["passed"]:
        print(
            f"QUALITY GATE FAILED: dead-letter ratio above {gate['max_dead_letter_ratio']}; "
            "clean_trades.csv not published",
            file=sys.stderr,
        )
    print(f"outputs written to {out_dir}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "feeds", nargs="+", type=Path, help="CSV feeds, processed in order (e.g. a feed, then replayed repairs)"
    )
    parser.add_argument("--out", type=Path, default=Path("out"), help="output directory (default: out)")
    parser.add_argument("--feed-date", type=date.fromisoformat, help="UTC date for time-only timestamps, YYYY-MM-DD")
    parser.add_argument("--max-clock-skew", type=float, default=30, metavar="SECONDS")
    parser.add_argument("--max-ingestion-lag", type=float, default=60, metavar="SECONDS")
    parser.add_argument("--dedup-horizon", type=float, default=24, metavar="HOURS")
    parser.add_argument("--strict-identifiers", action="store_true", help="require full-length 0x identifiers")
    parser.add_argument(
        "--max-dead-letter-ratio",
        type=float,
        metavar="RATIO",
        help="fail (exit 1) and withhold clean output above this ratio",
    )
    args = parser.parse_args(argv)

    config = Config(
        feed_date=args.feed_date,
        max_clock_skew=timedelta(seconds=args.max_clock_skew),
        max_ingestion_lag=timedelta(seconds=args.max_ingestion_lag),
        dedup_horizon=timedelta(hours=args.dedup_horizon),
        now=datetime.now(timezone.utc),
        strict_identifiers=args.strict_identifiers,
    )
    outputs = {(args.out / name).resolve() for name in OUTPUT_FILES}
    if any(feed.resolve() in outputs for feed in args.feeds):
        parser.error("an input feed is also an output file")
    try:
        results = validate(args.feeds, config)
    except (FeedError, ConfigError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    report = build_report(results, args.max_dead_letter_ratio)
    report["inputs"] = [str(feed) for feed in args.feeds]
    publish(results, report, args.out)
    _print_summary(results, report, args.out)
    return 0 if report["quality_gate"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
