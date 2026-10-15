"""Command line: validate a feed, resolve what can be resolved, write the results."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from .dummy_resolver import DummyChainResolver
from .output import CLEAN_FILE, DROPPED_FILE, QUARANTINE_FILE, write_outputs
from .parsing import FeedSchemaError
from .pipeline import Validator
from .resolution import resolve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m trade_feed_validator",
        description="Validate a trade event feed and route each row to clean, quarantine or dropped output.",
    )
    parser.add_argument("feed", type=Path, help="CSV feed to validate")
    parser.add_argument("--out-dir", type=Path, default=Path("out"), help="directory for output files (default: out)")
    args = parser.parse_args(argv)

    outputs = {(args.out_dir / name).resolve() for name in (CLEAN_FILE, QUARANTINE_FILE, DROPPED_FILE)}
    if args.feed.resolve() in outputs:
        print(f"error: {args.feed} would be overwritten by the output; choose another --out-dir", file=sys.stderr)
        return 1

    try:
        validator = Validator()
        validated = validator.validate_file(args.feed)
        resolved = resolve(validated.quarantined, DummyChainResolver(), validator)
        clean = validated.clean + resolved.loaded
        write_outputs(args.out_dir, clean, resolved.quarantined, resolved.dropped)
    except (OSError, UnicodeDecodeError, csv.Error, FeedSchemaError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    reasons = Counter(r for row in resolved.quarantined for r in row.reasons)
    total = len(clean) + len(resolved.quarantined) + len(resolved.dropped)
    print(f"{args.feed}: {total} rows")
    print(f"  clean        {len(clean)}")
    print(f"  quarantined  {len(resolved.quarantined)}")
    for reason, count in sorted(reasons.items()):
        print(f"    {reason:<24} {count}")
    print(f"  dropped      {len(resolved.dropped)}")
    print(f"Written to {args.out_dir}: {CLEAN_FILE}, {QUARANTINE_FILE}, {DROPPED_FILE}")
    return 0
