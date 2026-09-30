import csv
import json
from pathlib import Path

import pytest

from pipeline import main

SAMPLE = Path(__file__).resolve().parents[1] / "sample_feed.csv"
HEADER = "event_id,tx_hash,block_time,wallet,side,amount,ingested_at\n"


def run(tmp_path, *feeds, extra=()):
    out = tmp_path / "out"
    code = main([str(f) for f in feeds] + ["--feed-date", "2026-09-28", "--out", str(out), *extra])
    return code, out


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def read_clean(out):
    with open(out / "clean_trades.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_feed(tmp_path, body, name="feed.csv", header=HEADER, encoding="utf-8"):
    path = tmp_path / name
    path.write_text(header + body, encoding=encoding)
    return path


# --- the sample feed from the issue ------------------------------------------


@pytest.fixture
def sample(tmp_path):
    code, out = run(tmp_path, SAMPLE)
    assert code == 0
    return out


def test_sample_every_row_gets_exactly_one_outcome(sample):
    clean = [row["event_id"] for row in read_clean(sample)]
    dead = {r["event_id"]: r for r in read_jsonl(sample / "dead_letter.jsonl")}
    dups = {r["event_id"]: r for r in read_jsonl(sample / "duplicates.jsonl")}

    assert clean == ["evt_001", "evt_002", "evt_004", "evt_006"]
    assert dups["evt_003"]["reasons"] == ["duplicate_trade"] and dups["evt_003"]["related_event"] == "evt_002"
    assert dups["evt_007"]["reasons"] == ["duplicate_trade"] and dups["evt_007"]["related_event"] == "evt_006"
    assert dead["evt_005"]["reasons"] == ["missing_block_time"]
    assert dead["evt_008"]["reasons"] == ["block_time_after_ingestion"]
    assert sorted(clean + list(dead) + list(dups)) == [f"evt_00{i}" for i in range(1, 9)]


def test_sample_rejected_rows_keep_the_raw_record_for_repair(sample):
    [evt_005] = [r for r in read_jsonl(sample / "dead_letter.jsonl") if r["event_id"] == "evt_005"]
    assert evt_005["line"] == 6
    assert evt_005["raw"] == {
        "event_id": "evt_005",
        "tx_hash": "0xaa4",
        "block_time": "null",
        "wallet": "0xE5…",
        "side": "SELL",
        "amount": "30000",
        "ingested_at": "09:58:30",
    }


def test_sample_clean_output_is_normalised_and_in_chain_order(sample):
    rows = read_clean(sample)
    assert rows[0]["block_time"] == "2026-09-28T09:14:02Z"
    assert [r["block_time"] for r in rows] == sorted(r["block_time"] for r in rows)


def test_sample_report_shows_the_volume_the_naive_pipeline_would_inflate(sample):
    report = json.loads((sample / "report.json").read_text(encoding="utf-8"))
    assert (report["accepted"], report["duplicate"], report["dead_letter"]) == (4, 2, 2)
    assert report["volume"]["naive"] == {"BUY": "540000", "SELL": "165000", "total": "705000"}
    assert report["volume"]["clean"] == {"BUY": "330000", "SELL": "45000", "total": "375000"}
    assert report["volume"]["dead_letter"] == {"BUY": "0", "SELL": "120000", "total": "120000"}


def test_sample_repaired_dead_letter_can_be_replayed(tmp_path):
    # Hypothetical repair: block_time looked up on chain by tx_hash.
    repair = write_feed(tmp_path, "evt_005,0xaa4,09:58:25,0xE5…,SELL,30000,09:58:30\n", name="repair.csv")
    # Replayed twice: the second copy must not be double-counted.
    code, out = run(tmp_path, SAMPLE, repair, repair)
    assert code == 0
    clean = [row["event_id"] for row in read_clean(out)]
    assert clean == ["evt_001", "evt_002", "evt_004", "evt_005", "evt_006"]
    [replay] = [r for r in read_jsonl(out / "duplicates.jsonl") if r["event_id"] == "evt_005"]
    assert replay["reasons"] == ["duplicate_event_id"]


# --- malformed input ---------------------------------------------------------


def test_rows_with_wrong_field_count_are_dead_lettered_losslessly(tmp_path):
    feed = write_feed(tmp_path, "e1,0xa,09:00:00,0xd,BUY,1,09:00:01,surplus\ne2,0xb,09:00:00\n")
    code, out = run(tmp_path, feed)
    long_row, short_row = read_jsonl(out / "dead_letter.jsonl")
    assert long_row["reasons"] == ["malformed_row"] and long_row["extra_values"] == ["surplus"]
    assert short_row["reasons"] == ["malformed_row"] and short_row["raw"] == {
        "event_id": "e2",
        "tx_hash": "0xb",
        "block_time": "09:00:00",
    }
    assert read_clean(out) == []


def test_extra_columns_are_allowed_and_log_index_is_used(tmp_path):
    header = "venue,log_index," + HEADER
    feed = write_feed(
        tmp_path, "dex,0,e1,0xa,09:00:00,0xd,BUY,1,09:00:01\ndex,1,e2,0xa,09:00:00,0xd,BUY,1,09:00:01\n", header=header
    )
    code, out = run(tmp_path, feed)
    assert [(r["event_id"], r["log_index"]) for r in read_clean(out)] == [("e1", "0"), ("e2", "1")]


def test_utf8_bom_and_blank_lines_are_tolerated(tmp_path):
    feed = write_feed(tmp_path, "\ne1,0xa,09:00:00,0xd,BUY,1,09:00:01\n\n", encoding="utf-8-sig")
    code, out = run(tmp_path, feed)
    assert code == 0 and len(read_clean(out)) == 1


@pytest.mark.parametrize(
    "header",
    [
        "event_id,tx_hash,block_time,wallet,side,amount\n",
        "event_id,event_id,tx_hash,block_time,wallet,side,amount,ingested_at\n",
        "",
    ],
    ids=["missing_column", "repeated_column", "empty_file"],
)
def test_unusable_header_rejects_the_whole_feed(tmp_path, header):
    feed = write_feed(tmp_path, "", header=header)
    code, out = run(tmp_path, feed)
    assert code == 2
    assert not out.exists()


def test_non_utf8_feed_is_rejected(tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_bytes(HEADER.encode() + b"e1,0xa,09:00:00,0x\xff,BUY,1,09:00:01\n")
    code, _ = run(tmp_path, feed)
    assert code == 2


def test_time_only_feed_without_feed_date_is_a_usage_error(tmp_path):
    code = main([str(SAMPLE), "--out", str(tmp_path / "out")])
    assert code == 2


def test_input_that_is_also_an_output_is_refused(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    feed = write_feed(out, "e1,0xa,09:00:00,0xd,BUY,1,09:00:01\n", name="clean_trades.csv")
    with pytest.raises(SystemExit):
        main([str(feed), "--feed-date", "2026-09-28", "--out", str(out)])
    assert feed.exists()


# --- quality gate --------------------------------------------------------------


def test_quality_gate_withholds_clean_output(tmp_path):
    code, out = run(tmp_path, SAMPLE)
    assert (out / "clean_trades.csv").exists()

    # Same output directory: a stale clean file from the passing run must not survive.
    code, out = run(tmp_path, SAMPLE, extra=["--max-dead-letter-ratio", "0.1"])
    assert code == 1
    assert not (out / "clean_trades.csv").exists()
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert report["quality_gate"] == {"max_dead_letter_ratio": 0.1, "passed": False}
    assert len(read_jsonl(out / "dead_letter.jsonl")) == 2


def test_quality_gate_passes_under_threshold(tmp_path):
    code, _ = run(tmp_path, SAMPLE, extra=["--max-dead-letter-ratio", "0.25"])
    assert code == 0
