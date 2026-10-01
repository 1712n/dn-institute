package validator

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestValidateSampleFeedFindsAndHandlesAllKnownIssues(t *testing.T) {
	report, err := ValidateFeed(filepath.Join("..", "..", "sample_feed.csv"))
	if err != nil {
		t.Fatalf("ValidateFeed() error = %v", err)
	}
	if got, want := len(report.Accepted), 4; got != want {
		t.Errorf("accepted trades = %d, want %d", got, want)
	}
	if got, want := report.Quarantined, 2; got != want {
		t.Errorf("quarantined records = %d, want %d", got, want)
	}
	if got, want := report.Skipped, 2; got != want {
		t.Errorf("skipped duplicates = %d, want %d", got, want)
	}
	if got, want := len(report.QuarantineRecords), 2; got != want {
		t.Fatalf("quarantine records = %d, want %d", got, want)
	}
	if got, want := report.QuarantineRecords[0].EventID, "evt_005"; got != want {
		t.Errorf("first quarantined event = %q, want %q", got, want)
	}
	if got := report.QuarantineRecords[0].Raw[2]; got != "" {
		t.Errorf("evt_005 raw block_time = %q, want empty value preserved", got)
	}
	if got, want := len(report.SkippedRecords), 2; got != want {
		t.Errorf("skipped records = %d, want %d", got, want)
	}

	wantIssues := map[string]int{
		"duplicate_trade":       2,
		"missing_block_time":    1,
		"ingested_before_block": 1,
	}
	for _, issue := range report.Issues {
		if wantIssues[issue.Code] == 0 {
			t.Errorf("unexpected issue: %+v", issue)
			continue
		}
		wantIssues[issue.Code]--
	}
	for code, remaining := range wantIssues {
		if remaining != 0 {
			t.Errorf("issue %q missing %d time(s)", code, remaining)
		}
	}
}

func TestValidateFeedRejectsInvalidRows(t *testing.T) {
	tests := []struct {
		name string
		row  string
		code string
	}{
		{"missing event id", ",tx,09:00:00,wallet,BUY,10,09:00:01", "missing_identifier"},
		{"invalid block time", "evt,tx,not-a-time,wallet,BUY,10,09:00:01", "invalid_block_time"},
		{"invalid side", "evt,tx,09:00:00,wallet,HOLD,10,09:00:01", "invalid_side"},
		{"non-positive amount", "evt,tx,09:00:00,wallet,BUY,0,09:00:01", "invalid_amount"},
		{"invalid ingestion time", "evt,tx,09:00:00,wallet,BUY,10,nope", "invalid_ingested_at"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			filename := writeFeed(t, tt.row)
			report, err := ValidateFeed(filename)
			if err != nil {
				t.Fatalf("ValidateFeed() error = %v", err)
			}
			if report.Quarantined != 1 || len(report.Accepted) != 0 {
				t.Fatalf("unexpected report: %+v", report)
			}
			for _, issue := range report.Issues {
				if issue.Code == tt.code {
					return
				}
			}
			t.Errorf("issue %q not found in %+v", tt.code, report.Issues)
		})
	}
}

func TestValidateFeedRejectsWrongHeader(t *testing.T) {
	filename := writeRawFeed(t, "event_id,tx_hash\none,two")
	_, err := ValidateFeed(filename)
	if err == nil || !strings.Contains(err.Error(), "header") {
		t.Fatalf("ValidateFeed() error = %v, want header error", err)
	}
}

func TestValidateFeedRejectsMalformedCSV(t *testing.T) {
	filename := writeRawFeed(t, "event_id,tx_hash,block_time,wallet,side,amount,ingested_at\n\"unfinished")
	_, err := ValidateFeed(filename)
	if err == nil || !strings.Contains(err.Error(), "read") {
		t.Fatalf("ValidateFeed() error = %v, want CSV read error", err)
	}
}

func writeFeed(t *testing.T, row string) string {
	t.Helper()
	return writeRawFeed(t, strings.Join(expectedHeader, ",")+"\n"+row)
}

func writeRawFeed(t *testing.T, contents string) string {
	t.Helper()
	filename := filepath.Join(t.TempDir(), "feed.csv")
	if err := os.WriteFile(filename, []byte(contents), 0o600); err != nil {
		t.Fatalf("write test feed: %v", err)
	}
	return filename
}
