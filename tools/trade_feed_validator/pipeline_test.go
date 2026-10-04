package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestRunPipelineCreatesOutputDirectoryAndFiles(t *testing.T) {
	outputDir := filepath.Join(t.TempDir(), "nested", "output")
	result, err := runPipeline("sample_feed.csv", outputDir)
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Accepted) != 4 || len(result.Rejected) != 4 {
		t.Fatalf("accepted=%d rejected=%d, want 4 and 4", len(result.Accepted), len(result.Rejected))
	}

	for _, name := range []string{validOutputName, dlqOutputName, reportOutputName} {
		path := filepath.Join(outputDir, name)
		info, err := os.Stat(path)
		if err != nil {
			t.Errorf("output %s: %v", name, err)
			continue
		}
		if info.Size() == 0 {
			t.Errorf("output %s is empty", name)
		}
	}

	reportData, err := os.ReadFile(filepath.Join(outputDir, reportOutputName))
	if err != nil {
		t.Fatal(err)
	}
	var report validationReport
	if err := json.Unmarshal(reportData, &report); err != nil {
		t.Fatalf("decode validation report: %v", err)
	}
	if report.Summary.InputRows != 8 || report.Summary.AcceptedRows != 4 || report.Summary.RejectedRows != 4 {
		t.Errorf("unexpected report summary: %+v", report.Summary)
	}
	if report.Amounts.ParseableInput != "705000" || report.Amounts.Accepted != "375000" {
		t.Errorf("unexpected report amounts: %+v", report.Amounts)
	}
	wantIssues := map[string]int{
		"duplicate_trade":              2,
		"missing_block_time":           1,
		"block_time_after_ingested_at": 1,
	}
	for code, want := range wantIssues {
		if got := report.IssueCounts[code]; got != want {
			t.Errorf("issue count %s = %d, want %d", code, got, want)
		}
	}
}
