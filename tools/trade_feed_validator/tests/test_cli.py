import csv
import subprocess
import sys
from pathlib import Path

import pytest

from trade_feed_validator import output
from trade_feed_validator.cli import main
from trade_feed_validator.parsing import COLUMNS

SAMPLE = Path(__file__).parent.parent / "sample_feed.csv"


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_sample_run_writes_every_output_and_summary(tmp_path, capsys):
    assert main([str(SAMPLE), "--out-dir", str(tmp_path)]) == 0

    clean = {r["event_id"]: r for r in read(tmp_path / "clean.csv")}
    assert list(clean) == ["evt_001", "evt_002", "evt_004", "evt_006", "evt_005", "evt_007", "evt_008"]
    assert clean["evt_001"]["block_time"] == "09:14:02"
    assert clean["evt_001"]["amount"] == "120000"
    assert {e: r["flags"] for e, r in clean.items() if r["flags"]} == {
        "evt_005": "block_time_backfilled",
        "evt_007": "confirmed_distinct_trade",
        "evt_008": "ingested_at_unreliable",
    }
    assert clean["evt_005"]["block_time"] == "09:58:27"

    assert read(tmp_path / "quarantine.csv") == []
    [dropped] = read(tmp_path / "dropped.csv")
    assert (dropped["line"], dropped["event_id"], dropped["drop_reason"]) == ("4", "evt_003", "duplicate_confirmed")

    out = capsys.readouterr().out
    assert "8 rows" in out
    assert "clean        7" in out and "quarantined  0" in out and "dropped      1" in out


def test_rows_left_unresolved_are_written_to_quarantine_as_read(tmp_path):
    feed = tmp_path / "feed.csv"
    rows = [
        "evt_a,0xbb1,2026-01-01T09:00:00Z,0xD4…,BUY,100,2026-01-01T09:00:03Z",
        "evt_b,0xbb1,2026-01-01T09:00:00Z,0xD4…,BUY,100,2026-01-01T09:00:09Z",
        "evt_c,0xbb2,null,0xD4…,SELL,50,2026-01-01T09:01:00Z",
    ]
    feed.write_text(",".join(COLUMNS) + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    assert main([str(feed), "--out-dir", str(tmp_path / "out")]) == 0

    quarantine = {r["event_id"]: r for r in read(tmp_path / "out" / "quarantine.csv")}
    assert {e: r["reasons"] for e, r in quarantine.items()} == {
        "evt_b": "suspected_duplicate",
        "evt_c": "missing_required_value",
    }
    assert (quarantine["evt_b"]["line"], quarantine["evt_b"]["details"]) == ("3", "same trade as evt_a")
    assert quarantine["evt_c"]["block_time"] == "null"  # raw value, as read
    assert quarantine["evt_c"]["details"] == "block_time"


def test_module_command_runs_as_documented(tmp_path):
    tool_dir = SAMPLE.parent
    command = [sys.executable, "-m", "trade_feed_validator", "sample_feed.csv", "--out-dir", str(tmp_path)]
    done = subprocess.run(command, cwd=tool_dir, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert "8 rows" in done.stdout


def test_rerun_replaces_every_output(tmp_path):
    main([str(SAMPLE), "--out-dir", str(tmp_path)])
    feed = tmp_path / "feed.csv"
    feed.write_text(SAMPLE.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")
    assert main([str(feed), "--out-dir", str(tmp_path)]) == 0
    for name in ("clean.csv", "quarantine.csv", "dropped.csv"):
        assert read(tmp_path / name) == []


def test_input_columns_outside_the_schema_are_not_copied(tmp_path):
    feed = tmp_path / "feed.csv"
    header = ",".join(COLUMNS) + ",reasons"
    row = "evt_001,0xaa1,null,0xD4…,BUY,100,2026-01-01T09:00:00Z,spoofed"
    feed.write_text(f"{header}\n{row},surplus\n", encoding="utf-8")
    assert main([str(feed), "--out-dir", str(tmp_path / "out")]) == 0
    [held] = read(tmp_path / "out" / "quarantine.csv")
    assert held["reasons"] == "malformed_row"
    assert list(held) == ["line", *COLUMNS, "reasons", "details", "flags"]


def test_failed_write_keeps_the_previous_output_set(tmp_path, monkeypatch, capsys):
    out_dir = tmp_path / "out"
    main([str(SAMPLE), "--out-dir", str(out_dir)])
    before = {p.name: p.read_text(encoding="utf-8") for p in out_dir.iterdir()}

    write = output._write

    def fail_on_quarantine(path, header, rows):
        if path.name.startswith(".quarantine"):
            raise OSError("disk full")
        write(path, header, rows)

    monkeypatch.setattr(output, "_write", fail_on_quarantine)
    feed = tmp_path / "feed.csv"
    feed.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")
    assert main([str(feed), "--out-dir", str(out_dir)]) == 1
    assert "disk full" in capsys.readouterr().err
    assert {p.name: p.read_text(encoding="utf-8") for p in out_dir.iterdir()} == before


@pytest.mark.parametrize("name", ["clean.csv", ".quarantine.csv.tmp"], ids=["output file", "temporary file"])
def test_feed_at_an_output_path_is_not_overwritten(tmp_path, capsys, name):
    feed = tmp_path / name
    feed.write_text(SAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    assert main([str(feed), "--out-dir", str(tmp_path)]) == 1
    assert "would be overwritten" in capsys.readouterr().err
    assert feed.read_text(encoding="utf-8") == SAMPLE.read_text(encoding="utf-8")


def test_missing_feed_fails_with_a_message(tmp_path, capsys):
    assert main([str(tmp_path / "nope.csv"), "--out-dir", str(tmp_path)]) == 1
    assert "error:" in capsys.readouterr().err
    assert not (tmp_path / "clean.csv").exists()


def test_feed_without_required_columns_fails_with_a_message(tmp_path, capsys):
    feed = tmp_path / "feed.csv"
    feed.write_text("event_id,tx_hash\nevt_001,0xaa1\n", encoding="utf-8")
    assert main([str(feed), "--out-dir", str(tmp_path)]) == 1
    assert "missing columns" in capsys.readouterr().err


def test_non_utf8_feed_fails_with_a_message(tmp_path, capsys):
    feed = tmp_path / "feed.csv"
    feed.write_bytes(",".join(COLUMNS).encode() + b"\n\xff\xfe\n")
    assert main([str(feed), "--out-dir", str(tmp_path)]) == 1
    assert "error:" in capsys.readouterr().err
