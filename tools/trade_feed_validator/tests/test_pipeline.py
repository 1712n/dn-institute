"""The command-line pipeline: outputs, exit codes and failure modes."""

import csv
import json

import pytest

from pipeline import EXIT_BAD_INPUT, EXIT_OK, EXIT_QUALITY_GATE, main
from tests.support import HEADER, SAMPLE


def run(tmp_path, *extra, feed=SAMPLE):
    out = tmp_path / "out"
    code = main([str(feed), "--feed-date", "2026-09-28", "--out-dir", str(out), *extra])
    return code, out


def test_sample_end_to_end_writes_three_outputs(tmp_path):
    code, out = run(tmp_path)
    assert code == EXIT_OK

    with (out / "clean_trades.csv").open(newline="") as fh:
        clean = list(csv.DictReader(fh))
    assert [r["event_id"] for r in clean] == ["evt_001", "evt_002", "evt_004", "evt_006"]
    assert clean[0]["block_time"] == "2026-09-28T09:14:02Z"
    assert clean[3]["flags"] == "round_trip_suspect"

    dead = [json.loads(line) for line in (out / "dead_letter.jsonl").read_text().splitlines()]
    assert [d["event_id"] for d in dead] == ["evt_005", "evt_008"]
    assert dead[0]["raw"]["block_time"] == "null"

    report = json.loads((out / "report.json").read_text())
    assert report["counts"] == {"rows": 8, "accepted": 4, "duplicate": 2, "dead_letter": 2}
    assert report["round_trips"][0]["legs"] == ["evt_006", "evt_008"]


def test_quality_gate_fails_when_too_many_rows_are_dead_lettered(tmp_path):
    code, _ = run(tmp_path, "--max-dead-letter-rate", "0.2")  # sample: 2 of 8 = 25%
    assert code == EXIT_QUALITY_GATE


def test_quality_gate_passes_under_threshold(tmp_path):
    code, _ = run(tmp_path, "--max-dead-letter-rate", "0.25")
    assert code == EXIT_OK


def test_backfill_file_repairs_null_block_time(tmp_path):
    backfill = tmp_path / "backfill.csv"
    backfill.write_text("tx_hash,block_time\n0xAA4,2026-09-28T09:58:01Z\n")
    code, out = run(tmp_path, "--backfill", str(backfill))
    assert code == EXIT_OK
    report = json.loads((out / "report.json").read_text())
    assert report["counts"]["accepted"] == 5


@pytest.mark.parametrize(
    "header",
    [
        "event_id,tx_hash,block_time,wallet,side,amount",  # ingested_at missing
        HEADER + ",amount",  # repeated column
        "",  # empty file
    ],
)
def test_broken_schema_fails_the_whole_feed(tmp_path, header):
    feed = tmp_path / "feed.csv"
    feed.write_text(header + "\n" if header else "")
    code, out = run(tmp_path, feed=feed)
    assert code == EXIT_BAD_INPUT
    assert not out.exists()


def test_invalid_utf8_fails_cleanly(tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_bytes(HEADER.encode() + b"\n\xff\xfe,0x1\n")
    code, _ = run(tmp_path, feed=feed)
    assert code == EXIT_BAD_INPUT


def test_input_is_never_overwritten_by_an_output(tmp_path):
    feed = tmp_path / "report.json"
    feed.write_text(SAMPLE.read_text())
    code = main([str(feed), "--out-dir", str(tmp_path)])
    assert code == EXIT_BAD_INPUT
    assert feed.read_text() == SAMPLE.read_text()


@pytest.mark.parametrize(
    "args",
    [
        ["--max-dead-letter-rate", "1.5"],
        ["--clock-skew-seconds", "-1"],
        ["--clock-skew-seconds", "nan"],
        ["--round-trip-window-minutes", "inf"],
    ],
)
def test_invalid_options_are_rejected(tmp_path, args):
    with pytest.raises(SystemExit):
        run(tmp_path, *args)


def test_failed_run_does_not_leave_previous_outputs_behind(tmp_path):
    code, out = run(tmp_path)
    assert code == EXIT_OK and (out / "report.json").exists()
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n")
    code, out = run(tmp_path, feed=bad)
    assert code == EXIT_BAD_INPUT
    assert list(out.iterdir()) == []


def test_input_is_protected_on_case_insensitive_file_systems(tmp_path):
    feed = tmp_path / "REPORT.JSON"
    feed.write_text(SAMPLE.read_text())
    main([str(feed), "--out-dir", str(tmp_path)])
    assert feed.read_text() == SAMPLE.read_text()


def test_byte_order_mark_does_not_break_the_header(tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_bytes(b"\xef\xbb\xbf" + SAMPLE.read_bytes())
    code, _ = run(tmp_path, feed=feed)
    assert code == EXIT_OK


@pytest.mark.parametrize(
    "line",
    ["e1,0x1,10:00:00,0xa,BUY," + "9" * 200_000 + ",10:00:01", "e1,0x1\0,0xa,BUY,5,10:00:00,10:00:01"],
    ids=["field_over_csv_limit", "nul_byte"],
)
def test_unreadable_rows_fail_the_feed_cleanly(tmp_path, line):
    feed = tmp_path / "feed.csv"
    feed.write_text(HEADER + "\n" + line + "\n")
    code, _ = run(tmp_path, feed=feed)
    assert code == EXIT_BAD_INPUT


def test_out_dir_that_is_a_file_fails_cleanly(tmp_path):
    code = main([str(SAMPLE), "--out-dir", str(SAMPLE)])
    assert code == EXIT_BAD_INPUT


def test_extra_columns_pass_through_to_clean_output(tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_text(HEADER + ",venue\ne1,0x1,10:00:00,0xa,BUY,5,10:00:01,uniswap\n")
    _, out = run(tmp_path, feed=feed)
    with (out / "clean_trades.csv").open(newline="") as fh:
        assert next(csv.DictReader(fh))["venue"] == "uniswap"


def test_unbalanced_quote_fails_the_feed_instead_of_swallowing_rows(tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_text(
        HEADER + '\ne1,"0xa,10:00:00,0xw,BUY,1,10:00:01\n'
        "e2,0xb,10:00:00,0xw,BUY,1,10:00:01\ne3,0xc,10:00:00,0xw,BUY,1,10:00:01\n"
    )
    code, _ = run(tmp_path, feed=feed)
    assert code == EXIT_BAD_INPUT


def test_failed_quality_gate_does_not_publish_clean_trades(tmp_path):
    code, out = run(tmp_path, "--max-dead-letter-rate", "0.2")
    assert code == EXIT_QUALITY_GATE
    assert not (out / "clean_trades.csv").exists()
    assert (out / "dead_letter.jsonl").exists() and (out / "report.json").exists()


def test_reserved_column_names_fail_the_feed(tmp_path):
    feed = tmp_path / "feed.csv"
    feed.write_text(HEADER + ",flags\ne1,0x1,10:00:00,0xa,BUY,5,10:00:01,x\n")
    code, _ = run(tmp_path, feed=feed)
    assert code == EXIT_BAD_INPUT


def test_conflicting_backfill_entries_are_rejected(tmp_path):
    backfill = tmp_path / "backfill.csv"
    backfill.write_text("tx_hash,block_time\n0xaa4,2026-09-28T09:58:01Z\n0xAA4,2026-09-28T09:57:00Z\n")
    code, _ = run(tmp_path, "--backfill", str(backfill))
    assert code == EXIT_BAD_INPUT
