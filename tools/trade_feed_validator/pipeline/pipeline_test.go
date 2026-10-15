package pipeline

import (
	"bytes"
	"encoding/csv"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"trade_feed_validator/models"
)

var feedDate = time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)

const header = "event_id,tx_hash,block_time,wallet,side,amount,ingested_at\n"

func process(t *testing.T, csvText string) *Result {
	t.Helper()
	result, err := NewPipeline(feedDate).Process(strings.NewReader(csvText))
	if err != nil {
		t.Fatalf("Process: %v", err)
	}
	return result
}

func rejectedCodes(result *Result) map[string][]models.Code {
	out := map[string][]models.Code{}
	for _, r := range result.DeadLetter {
		for _, e := range r.Errors {
			out[r.EventID()] = append(out[r.EventID()], e.Code)
		}
	}
	return out
}

func TestSampleFeed(t *testing.T) {
	result, err := NewPipeline(feedDate).ProcessFile("../sample_feed.csv")
	if err != nil {
		t.Fatalf("ProcessFile: %v", err)
	}

	var clean []string
	for _, e := range result.Clean {
		clean = append(clean, e.EventID)
	}
	if got, want := strings.Join(clean, ","), "evt_001,evt_002,evt_004,evt_006"; got != want {
		t.Errorf("clean events = %s, want %s", got, want)
	}

	want := map[string]models.Code{
		"evt_003": models.CodeRedeliveredDuplicate,
		"evt_005": models.CodeMissingBlockTime,
		"evt_007": models.CodeExactDuplicate,
		"evt_008": models.CodeBlockTimeAfterIngest,
	}
	got := rejectedCodes(result)
	if len(got) != len(want) {
		t.Fatalf("dead-lettered events = %v, want %v", got, want)
	}
	for id, code := range want {
		if len(got[id]) != 1 || got[id][0] != code {
			t.Errorf("%s: got %v, want [%s]", id, got[id], code)
		}
	}

	if result.RawVolume != 705000 {
		t.Errorf("raw volume = %d, want 705000", result.RawVolume)
	}
	if v := result.CleanVolume(); v != 375000 {
		t.Errorf("clean volume = %d, want 375000", v)
	}
}

func TestResultDoesNotDependOnRunDate(t *testing.T) {
	feed := header + "evt_1,0x1,23:59:59,0xA,BUY,1,23:59:58\n"
	for _, day := range []time.Time{feedDate, feedDate.AddDate(0, 0, 1), feedDate.AddDate(1, 0, 0)} {
		result, err := NewPipeline(day).Process(strings.NewReader(feed))
		if err != nil {
			t.Fatal(err)
		}
		if len(result.DeadLetter) != 1 || result.DeadLetter[0].Errors[0].Code != models.CodeBlockTimeAfterIngest {
			t.Errorf("date %s: expected block_time_after_ingested_at, got %+v", day.Format("2006-01-02"), result.DeadLetter)
		}
	}
}

func TestTimesAreAnchoredToFeedDate(t *testing.T) {
	result := process(t, header+"evt_1,0x1,09:14:02,0xA,BUY,1,09:14:05\n")
	want := time.Date(2026, 1, 1, 9, 14, 2, 0, time.UTC)
	if !result.Clean[0].BlockTime.Equal(want) {
		t.Errorf("block_time = %s, want %s", result.Clean[0].BlockTime, want)
	}

	_, err := NewPipeline(time.Time{}).Process(strings.NewReader(header + "evt_1,0x1,09:14:02,0xA,BUY,1,09:14:05\n"))
	if !errors.Is(err, ErrFeedDateRequired) {
		t.Errorf("time-only feed without a feed date: got %v, want ErrFeedDateRequired", err)
	}
	full, err := NewPipeline(time.Time{}).Process(strings.NewReader(header + "evt_1,0x1,2026-03-05T09:14:02Z,0xA,BUY,1,2026-03-05T09:14:05Z\n"))
	if err != nil || len(full.Clean) != 1 {
		t.Errorf("full timestamps must not need a feed date: err %v, result %+v", err, full)
	}
}

func TestRFC3339TimestampsAreAccepted(t *testing.T) {
	result := process(t, header+"evt_1,0x1,2026-03-05T09:14:02Z,0xA,BUY,1,2026-03-05T09:14:05Z\n")
	if len(result.Clean) != 1 {
		t.Fatalf("expected 1 clean event, dead letter: %+v", result.DeadLetter)
	}
}

func TestColumnsAreMatchedByName(t *testing.T) {
	feed := "\ufeffingested_at,amount,side,wallet,block_time,tx_hash,event_id\n" + // leading BOM, as Excel writes it
		"09:14:05,120000,BUY,0xD4,09:14:02,0xaa1,evt_001\n"
	result := process(t, feed)
	if len(result.Clean) != 1 || result.Clean[0].EventID != "evt_001" || result.Clean[0].Amount != 120000 {
		t.Fatalf("unexpected result: %+v", result)
	}
}

func TestMissingHeaderColumnIsAnError(t *testing.T) {
	_, err := NewPipeline(feedDate).Process(strings.NewReader("event_id,tx_hash\nevt_1,0x1\n"))
	if err == nil || !strings.Contains(err.Error(), "block_time") {
		t.Fatalf("expected missing columns error, got %v", err)
	}

	_, err = NewPipeline(feedDate).Process(strings.NewReader(strings.TrimSuffix(header, "\n") + ",amount\n"))
	if err == nil || !strings.Contains(err.Error(), "duplicate column") {
		t.Fatalf("expected duplicate column error, got %v", err)
	}
}

func TestBadRowsGoToDeadLetterWithoutStoppingThePipeline(t *testing.T) {
	feed := header +
		"\n" + // blank line, skipped by the CSV reader but counted in line numbers
		"evt_1,0x1,09:00:00,0xA,BUY\n" + // too few fields
		"evt_2,0x2,09:00:00,0xA,BUY,12.5,09:00:01\n" + // not an integer
		"evt_3,0x3,9am,0xA,BUY,10,09:00:01\n" + // bad timestamp
		"evt_5,0x5,09:00:00,0xA,BUY,10,09:00:01,extra\n" + // more fields than the header
		"evt_4,0x4,09:00:00,0xA,sell,10,09:00:01\n" // lower-case side is normalized
	result := process(t, feed)

	want := map[string]models.Code{
		"evt_1": models.CodeMalformedRow,
		"evt_2": models.CodeInvalidAmount,
		"evt_3": models.CodeInvalidTimestamp,
		"evt_5": models.CodeMalformedRow,
	}
	got := rejectedCodes(result)
	for id, code := range want {
		if len(got[id]) != 1 || got[id][0] != code {
			t.Errorf("%s: got %v, want [%s]", id, got[id], code)
		}
	}
	if len(result.Clean) != 1 || result.Clean[0].EventID != "evt_4" || result.Clean[0].Side != models.SideSell {
		t.Errorf("expected only evt_4 to be clean, got %+v", result.Clean)
	}
	for i, r := range result.DeadLetter {
		if want := i + 3; r.Line != want {
			t.Errorf("%s: line = %d, want physical line %d", r.EventID(), r.Line, want)
		}
	}
}

func TestInvalidCSVRowIsDeadLetteredAndProcessingContinues(t *testing.T) {
	feed := header +
		"evt_1,0x1,09:00:00,0xA,BUY,10,09:00:01\n" +
		"\n" +
		"evt_2,0x\"2,09:00:00,0xA,BUY,10,09:00:01\n" + // bare quote inside a field
		"evt_3,0x3,09:00:00,0xA,SELL,10,09:00:01\n"
	result := process(t, feed)

	if len(result.Clean) != 2 || result.Clean[0].EventID != "evt_1" || result.Clean[1].EventID != "evt_3" {
		t.Fatalf("expected evt_1 and evt_3 to be clean, got %+v", result.Clean)
	}
	if len(result.DeadLetter) != 1 {
		t.Fatalf("expected 1 dead-lettered row, got %+v", result.DeadLetter)
	}
	r := result.DeadLetter[0]
	if r.Line != 4 || len(r.Errors) != 1 || r.Errors[0].Code != models.CodeMalformedRow {
		t.Errorf("got line %d errors %+v, want line 4 malformed_row", r.Line, r.Errors)
	}
	if want := "evt_2,0x\"2,09:00:00,0xA,BUY,10,09:00:01"; r.RawLine != want {
		t.Errorf("raw line = %q, want %q", r.RawLine, want)
	}
}

func TestNullVariantsAreTreatedAsMissing(t *testing.T) {
	feed := header +
		"evt_1,0x1,,0xA,BUY,10,09:00:01\n" +
		"evt_2,0x2,NULL,0xA,BUY,10,09:00:01\n"
	got := rejectedCodes(process(t, feed))
	for _, id := range []string{"evt_1", "evt_2"} {
		if len(got[id]) != 1 || got[id][0] != models.CodeMissingBlockTime {
			t.Errorf("%s: got %v, want [missing_block_time]", id, got[id])
		}
	}
}

func TestNullEventIDIsMissingField(t *testing.T) {
	feed := header +
		"null,0x1,09:00:00,0xA,BUY,10,09:00:01\n" +
		"NULL,0x2,09:00:00,0xA,BUY,10,09:00:01\n"
	result := process(t, feed)
	if len(result.Clean) != 0 {
		t.Fatalf("expected no clean events, got %+v", result.Clean)
	}
	if len(result.DeadLetter) != 2 {
		t.Fatalf("expected 2 dead-lettered rows, got %d", len(result.DeadLetter))
	}
	for _, r := range result.DeadLetter {
		if len(r.Errors) != 1 || r.Errors[0].Code != models.CodeMissingField || r.Errors[0].Field != "event_id" {
			t.Errorf("line %d: got %+v, want missing_field on event_id", r.Line, r.Errors)
		}
	}
}

func TestWriteOutputs(t *testing.T) {
	result, err := NewPipeline(feedDate).ProcessFile("../sample_feed.csv")
	if err != nil {
		t.Fatal(err)
	}
	dir := t.TempDir()
	if err := WriteOutputs(dir, result); err != nil {
		t.Fatal(err)
	}

	entries, err := os.ReadDir(dir)
	if err != nil {
		t.Fatal(err)
	}
	var names []string
	for _, e := range entries {
		names = append(names, e.Name())
	}
	if strings.Join(names, ",") != "clean.csv,dead_letter.csv" {
		t.Errorf("output dir contains %v, want only clean.csv and dead_letter.csv", names)
	}
	for _, name := range names {
		info, err := os.Stat(filepath.Join(dir, name))
		if err != nil {
			t.Fatal(err)
		}
		if perm := info.Mode().Perm(); perm != 0o644 {
			t.Errorf("%s has permissions %o, want 644", name, perm)
		}
	}

	clean := readCSV(t, filepath.Join(dir, "clean.csv"))
	if len(clean) != 1+4 {
		t.Errorf("clean.csv has %d rows, want header + 4", len(clean))
	}
	if clean[1][2] != "2026-01-01T09:14:02Z" {
		t.Errorf("clean.csv block_time = %s, want full UTC timestamp", clean[1][2])
	}

	dead := readCSV(t, filepath.Join(dir, "dead_letter.csv"))
	if len(dead) != 1+4 {
		t.Fatalf("dead_letter.csv has %d rows, want header + 4", len(dead))
	}
	codeCol, rawCol := len(dead[0])-3, len(dead[0])-1
	if dead[0][codeCol] != "error_codes" || dead[0][rawCol] != "raw_line" {
		t.Fatalf("unexpected dead_letter header: %v", dead[0])
	}
	for _, row := range dead[1:] {
		if row[1] == "evt_005" {
			if row[3] != "null" || row[codeCol] != string(models.CodeMissingBlockTime) {
				t.Errorf("evt_005 must keep its raw values and reason, got %v", row)
			}
			if want := "evt_005,0xaa4,null,0xE5…,SELL,30000,09:58:30"; row[rawCol] != want {
				t.Errorf("evt_005 raw_line = %q, want %q", row[rawCol], want)
			}
			return
		}
	}
	t.Error("evt_005 not found in dead_letter.csv")
}

func readCSV(t *testing.T, path string) [][]string {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	rows, err := csv.NewReader(bytes.NewReader(data)).ReadAll()
	if err != nil {
		t.Fatal(err)
	}
	return rows
}
