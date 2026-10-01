"""Run the trade feed validator over a CSV feed.

    python3 pipeline.py sample_feed.csv --out-dir output

Writes to ``--out-dir``:

* ``clean.csv``       - accepted events, sorted by block_time (chain order),
                        with a ``warnings`` column;
* ``duplicates.csv``  - dropped events and the event they duplicate;
* ``dead_letter.csv`` - rejected events with the reasons, ready to be fixed
                        and replayed;
* ``report.json``     - counts and volume before/after validation.

Raw values are written back unchanged so nothing is lost or reformatted.
Exit code is 0, or 1 with ``--fail-on-dead-letter`` if anything was rejected.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional, Sequence

from validator import DEFAULT_FEED_DATE, Decision, Severity, Status, TradeFeedValidator


def read_feed(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def _issues(decision: Decision, severity: Severity) -> str:
    return "; ".join(str(f) for f in decision.issues if f.severity is severity)


def _write(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _naive_volume(rows: list[dict[str, str]]) -> Decimal:
    """What the old ``parse -> insert`` pipeline would have summed."""
    total = Decimal(0)
    for row in rows:
        try:
            total += Decimal(row.get("amount") or "0")
        except InvalidOperation:
            pass
    return total


def run(
    feed_path: Path, out_dir: Path, feed_date: date = DEFAULT_FEED_DATE
) -> tuple[list[Decision], dict]:
    fieldnames, rows = read_feed(feed_path)
    decisions = TradeFeedValidator(feed_date=feed_date).process_all(rows)

    accepted = sorted(
        (d for d in decisions if d.status is Status.ACCEPTED),
        key=lambda d: (d.event.block_time, d.event_id),
    )
    duplicates = [d for d in decisions if d.status is Status.DUPLICATE]
    dead_letter = [d for d in decisions if d.status is Status.DEAD_LETTER]

    out_dir.mkdir(parents=True, exist_ok=True)
    _write(
        out_dir / "clean.csv",
        fieldnames + ["warnings"],
        [{**d.raw, "warnings": _issues(d, Severity.WARNING)} for d in accepted],
    )
    _write(
        out_dir / "duplicates.csv",
        fieldnames + ["duplicate_of", "reason"],
        [
            {
                **d.raw,
                "duplicate_of": d.duplicate_of,
                "reason": _issues(d, Severity.DUPLICATE),
            }
            for d in duplicates
        ],
    )
    _write(
        out_dir / "dead_letter.csv",
        fieldnames + ["errors", "warnings"],
        [
            {
                **d.raw,
                "errors": _issues(d, Severity.ERROR),
                "warnings": _issues(d, Severity.WARNING),
            }
            for d in dead_letter
        ],
    )

    report = {
        "input_events": len(rows),
        "accepted": len(accepted),
        "duplicates": len(duplicates),
        "dead_letter": len(dead_letter),
        "volume_naive": str(_naive_volume(rows)),
        "volume_validated": str(sum((d.event.amount for d in accepted), Decimal(0))),
        "decisions": [
            {
                "event_id": d.event_id,
                "status": d.status.value,
                "duplicate_of": d.duplicate_of,
                "issues": [
                    {
                        "issue": f.issue.value,
                        "severity": f.severity.value,
                        "message": f.message,
                    }
                    for f in d.issues
                ],
            }
            for d in decisions
        ],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return decisions, report


def print_summary(decisions: list[Decision], report: dict) -> None:
    for d in decisions:
        line = f"{d.event_id:<10} {d.status.value:<12}"
        if d.duplicate_of:
            line += f" duplicate_of={d.duplicate_of}"
        print(line)
        for f in d.issues:
            print(f"{'':<10} - [{f.severity.value}] {f}")
    print()
    print(
        f"input={report['input_events']} accepted={report['accepted']} "
        f"duplicates={report['duplicates']} dead_letter={report['dead_letter']}"
    )
    print(
        f"volume: naive={report['volume_naive']} "
        f"validated={report['volume_validated']}"
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("feed", type=Path, help="input CSV feed")
    parser.add_argument("--out-dir", type=Path, default=Path("output"))
    parser.add_argument(
        "--feed-date",
        type=date.fromisoformat,
        default=DEFAULT_FEED_DATE,
        help="date (YYYY-MM-DD) for time-only timestamps such as 09:14:02",
    )
    parser.add_argument(
        "--fail-on-dead-letter",
        action="store_true",
        help="exit with code 1 if any event was dead-lettered (for CI / alerting)",
    )
    args = parser.parse_args(argv)

    decisions, report = run(args.feed, args.out_dir, args.feed_date)
    print_summary(decisions, report)
    print(f"\nwritten to {args.out_dir}/")
    if args.fail_on_dead_letter and report["dead_letter"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
