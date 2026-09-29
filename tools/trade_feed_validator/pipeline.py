"""Trade feed validator: replaces ``insert_into(analytics_table, parse(event))``.

Every raw row gets exactly one outcome:

* ``accepted``    -> clean_trades.csv, canonical values, sorted by block_time, flags attached
* ``duplicate``   -> dropped, listed in report.json with the event it duplicates
* ``dead_letter`` -> dead_letter.jsonl with the raw row verbatim and reason codes, for repair and replay

Usage: python pipeline.py sample_feed.csv --feed-date 2026-09-28 --out-dir out
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

from records import (
    AMOUNT_PRECISION,
    LOG_INDEX_COLUMN,
    PLACEHOLDER_DATE,
    REJECT,
    REQUIRED_COLUMNS,
    BlockTimeResolver,
    FeedSchemaError,
    RawRow,
    TradeEvent,
    format_amount,
    is_null,
    is_time_only,
    normalize_id,
    parse_event,
    parse_timestamp,
    read_feed,
)
from rules import RECORD_RULES, Config, Deduplicator, OrderTracker, find_round_trips, utc

ACCEPTED, DUPLICATE, DEAD_LETTER = "accepted", "duplicate", "dead_letter"
CLEAN_FILE, DEAD_LETTER_FILE, REPORT_FILE = "clean_trades.csv", "dead_letter.jsonl", "report.json"

EXIT_OK, EXIT_BAD_INPUT, EXIT_QUALITY_GATE = 0, 1, 3


@dataclass
class Result:
    header: list[str]
    events: list[TradeEvent]
    outcome: dict[int, str]
    duplicate_of: dict[int, str]
    round_trips: list[tuple[TradeEvent, TradeEvent]]
    warnings: list[str] = field(default_factory=list)

    def by_outcome(self, outcome: str) -> list[TradeEvent]:
        return [e for e in self.events if self.outcome[e.row] == outcome]

    @property
    def accepted(self) -> list[TradeEvent]:
        """Accepted events in chain order, not arrival order."""
        return sorted(self.by_outcome(ACCEPTED), key=lambda e: (e.block_time, e.row))

    @property
    def dead_letters(self) -> list[TradeEvent]:
        return self.by_outcome(DEAD_LETTER)

    @property
    def duplicates(self) -> list[TradeEvent]:
        return self.by_outcome(DUPLICATE)

    def volume(self) -> dict[str, str]:
        def total(events: Iterable[TradeEvent]) -> str:
            with localcontext() as ctx:
                ctx.prec = AMOUNT_PRECISION  # exact: the default 28 digits would round wei-scale sums
                return format_amount(sum((e.amount for e in events if e.amount is not None), Decimal(0)))

        return {
            # what the old insert-everything pipeline would have reported
            "naive": total(self.events),
            "clean": total(self.by_outcome(ACCEPTED)),
            "dead_letter": total(self.dead_letters),
            "duplicate": total(self.duplicates),
        }

    def dead_letter_rate(self) -> float:
        return len(self.dead_letters) / len(self.events) if self.events else 0.0


def validate(
    raw_rows: list[RawRow],
    header: list[str],
    config: Config | None = None,
    feed_date: date | None = None,
    resolve_block_time: BlockTimeResolver | None = None,
) -> Result:
    """Run all checks over rows in arrival order, the way a stream consumer would."""
    config = config or Config()
    dedup, order = Deduplicator(), OrderTracker()
    events: list[TradeEvent] = []
    outcome: dict[int, str] = {}
    duplicate_of: dict[int, str] = {}

    for raw in raw_rows:
        ev = parse_event(raw, feed_date, resolve_block_time)
        for rule in RECORD_RULES:
            rule(ev, config)
        order.check_ingest_clock(ev, config)
        if not ev.rejected:
            original = dedup.check(ev)
            if original is not None:
                duplicate_of[ev.row] = original
        if ev.rejected:
            outcome[ev.row] = DEAD_LETTER
        elif ev.dropped:
            outcome[ev.row] = DUPLICATE
            dedup.reserve_event_id(ev)
            order.advance_ingest_clock(ev)
        else:
            outcome[ev.row] = ACCEPTED
            dedup.remember(ev)
            order.advance_ingest_clock(ev)
            order.observe_accepted(ev)
        events.append(ev)

    unique = [e for e in events if outcome[e.row] != DUPLICATE]
    round_trips = find_round_trips(unique, config)
    return Result(header, events, outcome, duplicate_of, round_trips, _feed_warnings(raw_rows, feed_date))


def _feed_warnings(raw_rows: list[RawRow], feed_date: date | None) -> list[str]:
    values = [
        r.fields.get(c)
        for r in raw_rows
        for c in ("block_time", "ingested_at")
        if not is_null(r.fields.get(c))
    ]
    kinds = {is_time_only(v) for v in values}
    warnings = []
    if True in kinds:
        anchor = (
            feed_date.isoformat()
            if feed_date
            else f"{PLACEHOLDER_DATE.isoformat()} (placeholder, pass --feed-date)"
        )
        warnings.append(
            f"time-only timestamps anchored to {anchor}; a trade near midnight UTC cannot be placed "
            "on the right day, the indexer should emit full ISO 8601 timestamps"
        )
    if not raw_rows:
        warnings.append("feed has a header but no rows; an empty delivery is itself worth an alert")
    if kinds == {True, False}:
        warnings.append("feed mixes time-only and full timestamps; ordering across the two is unreliable")
    return warnings


# ---------------------------------------------------------------- outputs

OUTPUT_FILES = (CLEAN_FILE, DEAD_LETTER_FILE, REPORT_FILE)


def render_outputs(result: Result, source: Path, config: Config) -> dict[str, str]:
    """Build all three outputs in memory first, so a failure writes nothing."""
    dead_letters = "".join(
        json.dumps(_dead_letter(e), ensure_ascii=False) + "\n" for e in result.dead_letters
    )
    report = json.dumps(_report(result, source, config), indent=2, ensure_ascii=False) + "\n"
    return {CLEAN_FILE: _clean_csv(result), DEAD_LETTER_FILE: dead_letters, REPORT_FILE: report}


def write_outputs(files: dict[str, str], out_dir: Path) -> None:
    """Each file goes to a unique temp name and is renamed into place, so a
    reader never sees a half-written file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=f".{name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            os.replace(tmp, out_dir / name)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise


def remove_outputs(out_dir: Path) -> None:
    """Called before a run, so a failed run cannot leave the previous run's files looking current."""
    for name in OUTPUT_FILES:
        (out_dir / name).unlink(missing_ok=True)


def _extra_columns(header: list[str]) -> list[str]:
    return [h for h in header if h not in REQUIRED_COLUMNS]


def _clean_csv(result: Result) -> str:
    extra = _extra_columns(result.header)  # log_index and any other columns pass through
    columns = [*REQUIRED_COLUMNS, *extra, "flags", "source_row"]
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(columns)
    for e in result.accepted:
        row = [
            e.event_id,
            e.tx_hash,
            utc(e.block_time),
            e.wallet,
            e.side,
            format_amount(e.amount),
            utc(e.ingested_at),
        ]
        row += [e.log_index if c == LOG_INDEX_COLUMN else e.raw.fields.get(c) for c in extra]
        row += [";".join(i.code for i in e.flags), e.row]
        writer.writerow(row)
    return buf.getvalue()


def _dead_letter(e: TradeEvent) -> dict:
    return {
        "source_row": e.row,
        "event_id": e.event_id,
        "reasons": [i.as_dict() for i in e.issues if i.severity == REJECT],
        "flags": [i.as_dict() for i in e.flags],
        "raw": e.raw.fields,  # as received, so a repaired row can be replayed through the same pipeline
        "raw_overflow": e.raw.overflow,
    }


def _report(result: Result, source: Path, config: Config) -> dict:
    return {
        "source": str(source),
        "config": {k: v.total_seconds() if isinstance(v, timedelta) else v for k, v in vars(config).items()},
        "counts": {
            "rows": len(result.events),
            ACCEPTED: len(result.by_outcome(ACCEPTED)),
            DUPLICATE: len(result.duplicates),
            DEAD_LETTER: len(result.dead_letters),
        },
        "volume": result.volume(),
        "warnings": result.warnings,
        "rows": [
            {
                "source_row": e.row,
                "event_id": e.event_id,
                "outcome": result.outcome[e.row],
                "duplicate_of": result.duplicate_of.get(e.row),
                "issues": [dict(i.as_dict(), severity=i.severity) for i in e.issues],
            }
            for e in result.events
        ],
        "round_trips": [
            {
                "wallet": a.wallet,
                "amount": format_amount(a.amount),
                "legs": [a.event_id, b.event_id],
                "gap_seconds": (b.block_time - a.block_time).total_seconds(),
            }
            for a, b in result.round_trips
        ],
    }


def render_summary(result: Result) -> str:
    lines = [f"{'row':>3}  {'event_id':<9} {'outcome':<11} issues"]
    for e in result.events:
        issues = "; ".join(i.code for i in e.issues) or "-"
        lines.append(f"{e.row:>3}  {e.event_id or '?':<9} {result.outcome[e.row]:<11} {issues}")
    v = result.volume()
    lines.append("")
    lines.append(
        f"volume: naive {v['naive']} -> clean {v['clean']} "
        f"(dead_letter {v['dead_letter']}, duplicate {v['duplicate']})"
    )
    for a, b in result.round_trips:
        lines.append(
            f"round trip: {a.wallet} {a.side} {a.event_id} -> {b.side} {b.event_id}, "
            f"amount {format_amount(a.amount)}"
        )
    lines.extend(f"warning: {w}" for w in result.warnings)
    return "\n".join(lines)


# ---------------------------------------------------------------- CLI


def load_backfill(path: Path, feed_date: date | None) -> dict[str, datetime]:
    """CSV with tx_hash,block_time. Stands in for a node RPC lookup of the block timestamp."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        table: dict[str, datetime] = {}
        for row in csv.DictReader(fh):
            value, err = parse_timestamp(row.get("block_time") or "", feed_date)
            if err or is_null(row.get("tx_hash")):
                raise FeedSchemaError(f"bad backfill row {row}: {err or 'empty tx_hash'}")
            tx_hash = normalize_id(row["tx_hash"])
            if table.get(tx_hash, value) != value:
                raise FeedSchemaError(f"backfill has two block times for {tx_hash}")
            table[tx_hash] = value
    return table


def _bounded_float(upper: float):
    def parse(text: str) -> float:
        value = float(text)
        if not math.isfinite(value) or not 0 <= value <= upper:
            raise argparse.ArgumentTypeError(f"must be a number between 0 and {upper:g}")
        return value

    return parse


def _same_file(a: Path, b: Path) -> bool:
    """True for the same file even on case-insensitive file systems or via links."""
    try:
        return a.exists() and b.exists() and os.path.samefile(a, b)
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("feed", type=Path, help="raw feed CSV")
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    parser.add_argument(
        "--feed-date", type=date.fromisoformat, help="UTC day for time-only timestamps, YYYY-MM-DD"
    )
    parser.add_argument("--backfill", type=Path, help="CSV tx_hash,block_time used to repair null block_time")
    parser.add_argument("--clock-skew-seconds", type=_bounded_float(86_400), default=5)
    parser.add_argument("--max-ingest-lag-seconds", type=_bounded_float(86_400 * 30), default=120)
    parser.add_argument("--round-trip-window-minutes", type=_bounded_float(60 * 24 * 30), default=30)
    parser.add_argument(
        "--strict-identifiers",
        action="store_true",
        help="require full EVM ids (20-byte wallet, 32-byte tx hash); the sample uses shortened ids",
    )
    parser.add_argument(
        "--max-dead-letter-rate",
        type=_bounded_float(1),
        help="quality gate: exit 3 when the share of dead-lettered rows is above this (0..1)",
    )
    args = parser.parse_args(argv)

    config = Config(
        clock_skew=timedelta(seconds=args.clock_skew_seconds),
        max_ingest_lag=timedelta(seconds=args.max_ingest_lag_seconds),
        round_trip_window=timedelta(minutes=args.round_trip_window_minutes),
        strict_identifiers=args.strict_identifiers,
    )

    def fail(message: str) -> int:
        print(f"error: {message}", file=sys.stderr)
        return EXIT_BAD_INPUT

    if args.out_dir.exists() and not args.out_dir.is_dir():
        return fail(f"--out-dir {args.out_dir} exists and is not a directory")
    for source in filter(None, (args.feed, args.backfill)):
        if any(_same_file(source, args.out_dir / name) for name in OUTPUT_FILES):
            return fail(f"input {source} would be overwritten by an output file")

    try:
        remove_outputs(args.out_dir)
        resolver = load_backfill(args.backfill, args.feed_date).get if args.backfill else None
        # utf-8-sig: a byte-order mark from a spreadsheet export must not break the header
        with args.feed.open(newline="", encoding="utf-8-sig") as fh:
            header, raw_rows = read_feed(fh)
        result = validate(raw_rows, header, config, args.feed_date, resolver)
        rate = result.dead_letter_rate()
        gate_failed = args.max_dead_letter_rate is not None and rate > args.max_dead_letter_rate
        files = render_outputs(result, args.feed, config)
        if gate_failed:
            del files[CLEAN_FILE]  # a batch that failed the gate must not reach analytics
        write_outputs(files, args.out_dir)
    except (OSError, UnicodeDecodeError, csv.Error, FeedSchemaError) as exc:
        return fail(str(exc))

    print(render_summary(result))
    print(f"\noutputs written to {args.out_dir}/")

    if gate_failed:
        print(
            f"quality gate failed: dead-letter rate {rate:.0%} > {args.max_dead_letter_rate:.0%}; "
            f"{CLEAN_FILE} not published",
            file=sys.stderr,
        )
        return EXIT_QUALITY_GATE
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
