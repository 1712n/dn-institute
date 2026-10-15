"""Write run results as CSV files.

Quarantined and dropped rows keep the schema columns exactly as read, plus the
source line number, so every decision traces back to the input. Columns
outside the schema aren't copied: our own columns then can't collide with
input column names, and the line number points to the full original row.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from .models import TIME_ONLY_DATE, QuarantinedRow, TradeEvent
from .parsing import COLUMNS
from .resolution import DroppedRow

CLEAN_FILE = "clean.csv"
QUARANTINE_FILE = "quarantine.csv"
DROPPED_FILE = "dropped.csv"
OUTPUT_FILES = (CLEAN_FILE, QUARANTINE_FILE, DROPPED_FILE)


def output_paths(out_dir: Path) -> list[Path]:
    """Every path a run writes to: the three output files and their temporary copies."""
    return [out_dir / n for name in OUTPUT_FILES for n in (name, _staging_name(name))]


def write_outputs(
    out_dir: Path,
    clean: Iterable[TradeEvent],
    quarantined: Iterable[QuarantinedRow],
    dropped: Iterable[DroppedRow],
) -> None:
    """Write all three files, even when empty, so none is left from an earlier run.

    Files are written under temporary names and renamed into place only once
    all three are complete, so a failed write leaves the previous set intact
    instead of mixing files from two runs.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        CLEAN_FILE: ([*COLUMNS, "flags"], map(_clean_row, clean)),
        QUARANTINE_FILE: (["line", *COLUMNS, "reasons", "details", "flags"], map(_quarantine_row, quarantined)),
        DROPPED_FILE: (["line", *COLUMNS, "drop_reason"], map(_dropped_row, dropped)),
    }
    staged = {name: out_dir / _staging_name(name) for name in files}
    try:
        for name, (header, rows) in files.items():
            _write(staged[name], header, rows)
    except BaseException:
        for tmp in staged.values():
            tmp.unlink(missing_ok=True)
        raise
    for name, tmp in staged.items():
        tmp.replace(out_dir / name)


def _staging_name(name: str) -> str:
    return f".{name}.tmp"


def _write(path: Path, header: list[str], rows: Iterable[list[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def _clean_row(event: TradeEvent) -> list[str]:
    return [
        event.event_id,
        event.tx_hash,
        _timestamp(event.block_time),
        event.wallet,
        event.side,
        format(event.amount, "f"),
        _timestamp(event.ingested_at),
        _join(event.flags),
    ]


def _quarantine_row(row: QuarantinedRow) -> list[str]:
    details = (": ".join(part for part in (v.field, v.detail) if part) for v in row.violations)
    flags = row.event.flags if row.event else ()
    return [
        str(row.line),
        *_raw_values(row),
        _join(row.reasons),
        "; ".join(details),
        _join(flags),
    ]


def _dropped_row(dropped: DroppedRow) -> list[str]:
    return [str(dropped.row.line), *_raw_values(dropped.row), dropped.reason]


def _raw_values(row: QuarantinedRow) -> list[str]:
    return [row.raw.get(c) or "" for c in COLUMNS]


def _timestamp(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.date() == TIME_ONLY_DATE:
        return value.strftime("%H:%M:%S")
    return value.isoformat().replace("+00:00", "Z")


def _join(codes: Iterable[str]) -> str:
    return ";".join(sorted(codes))
