"""Helpers shared by the test modules."""

import io
from datetime import date
from pathlib import Path

from pipeline import validate
from records import read_feed

HEADER = "event_id,tx_hash,block_time,wallet,side,amount,ingested_at"
SAMPLE = Path(__file__).resolve().parent.parent / "sample_feed.csv"
FEED_DATE = date(2026, 9, 28)


def run_csv(text, config=None, feed_date=FEED_DATE, resolver=None):
    header, rows = read_feed(io.StringIO(text))
    return validate(rows, header, config, feed_date, resolver)


def run_rows(*rows, header=HEADER, **kwargs):
    return run_csv("\n".join([header, *rows]) + "\n", **kwargs)


def by_id(result, event_id):
    return next(e for e in result.events if e.event_id == event_id)


def codes(event):
    return {i.code for i in event.issues}
