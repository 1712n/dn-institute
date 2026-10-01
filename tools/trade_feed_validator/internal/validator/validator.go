package validator

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

var expectedHeader = []string{
	"event_id", "tx_hash", "block_time", "wallet", "side", "amount", "ingested_at",
}

type Trade struct {
	EventID    string    `json:"event_id"`
	TxHash     string    `json:"tx_hash"`
	BlockTime  string    `json:"block_time_utc"`
	Wallet     string    `json:"wallet"`
	Side       string    `json:"side"`
	Amount     int64     `json:"amount"`
	IngestedAt string    `json:"ingested_at_utc"`
}

type Issue struct {
	Row         int    `json:"csv_line"`
	EventID     string `json:"event_id,omitempty"`
	Code        string `json:"code"`
	Message     string `json:"message"`
	Disposition string `json:"disposition"`
}

type RejectedRecord struct {
	Row     int      `json:"csv_line"`
	EventID string   `json:"event_id,omitempty"`
	Raw     []string `json:"raw_fields"`
	Issues  []Issue  `json:"issues"`
}

type Report struct {
	Accepted          []Trade          `json:"accepted"`
	Quarantined       int              `json:"quarantined_count"`
	Skipped           int              `json:"skipped_duplicate_count"`
	QuarantineRecords []RejectedRecord `json:"quarantine_records"`
	SkippedRecords    []RejectedRecord `json:"skipped_duplicates"`
	Issues            []Issue          `json:"issues"`
}

func ValidateFeed(filename string) (Report, error) {
	file, err := os.Open(filename)
	if err != nil {
		return Report{}, fmt.Errorf("open %q: %w", filename, err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	rows, err := reader.ReadAll()
	if err != nil {
		return Report{}, fmt.Errorf("read %q: %w", filename, err)
	}
	if len(rows) == 0 {
		return Report{}, fmt.Errorf("%q is empty", filename)
	}
	if len(rows[0]) != len(expectedHeader) {
		return Report{}, fmt.Errorf("unexpected number of header columns: got %d, want %d", len(rows[0]), len(expectedHeader))
	}
	for i, expected := range expectedHeader {
		if strings.TrimSpace(rows[0][i]) != expected {
			return Report{}, fmt.Errorf("unexpected header column %d: got %q, want %q", i+1, rows[0][i], expected)
		}
	}
	if len(rows) == 1 {
		return Report{}, fmt.Errorf("%q has no data rows", filename)
	}

	report := Report{Accepted: make([]Trade, 0, len(rows)-1)}
	seen := make(map[string]struct{}, len(rows)-1)
	for i, row := range rows[1:] {
		line := i + 2
		rawRow := append([]string(nil), row...)
		issueStart := len(report.Issues)
		if len(row) != len(expectedHeader) {
			issue := Issue{Row: line, Code: "column_count", Message: fmt.Sprintf("got %d columns, want %d", len(row), len(expectedHeader)), Disposition: "quarantine"}
			addIssue(&report, issue)
			report.Quarantined++
			report.QuarantineRecords = append(report.QuarantineRecords, RejectedRecord{Row: line, Raw: rawRow, Issues: []Issue{issue}})
			continue
		}
		for j := range row {
			row[j] = strings.TrimSpace(row[j])
		}
		trade := Trade{EventID: row[0], TxHash: row[1], Wallet: row[3], Side: strings.ToUpper(row[4])}
		bad := false
		if trade.EventID == "" || trade.TxHash == "" || trade.Wallet == "" {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "missing_identifier", Message: "event_id, tx_hash, and wallet are required", Disposition: "quarantine"})
			bad = true
		}
		if row[2] == "" {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "missing_block_time", Message: "block_time is required; cannot safely place this trade in time", Disposition: "quarantine"})
			bad = true
		} else if _, err = parseTime(row[2]); err != nil {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "invalid_block_time", Message: fmt.Sprintf("invalid block_time %q (want HH:MM:SS)", row[2]), Disposition: "quarantine"})
			bad = true
		} else {
			trade.BlockTime = row[2]
		}
		if trade.Side != "BUY" && trade.Side != "SELL" {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "invalid_side", Message: fmt.Sprintf("side must be BUY or SELL, got %q", row[4]), Disposition: "quarantine"})
			bad = true
		}
		if trade.Amount, err = strconv.ParseInt(row[5], 10, 64); err != nil || trade.Amount <= 0 {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "invalid_amount", Message: fmt.Sprintf("amount must be a positive integer, got %q", row[5]), Disposition: "quarantine"})
			bad = true
		}
		if row[6] == "" {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "missing_ingested_at", Message: "ingested_at is required", Disposition: "quarantine"})
			bad = true
		} else if _, err = parseTime(row[6]); err != nil {
			addIssue(&report, Issue{Row: line, EventID: trade.EventID, Code: "invalid_ingested_at", Message: fmt.Sprintf("invalid ingested_at %q (want HH:MM:SS)", row[6]), Disposition: "quarantine"})
			bad = true
		} else {
			trade.IngestedAt = row[6]
		}
		if bad {
			report.Quarantined++
			report.QuarantineRecords = append(report.QuarantineRecords, RejectedRecord{
				Row: line, EventID: trade.EventID, Raw: rawRow,
				Issues: append([]Issue(nil), report.Issues[issueStart:]...),
			})
			continue
		}
		ingestedAt, _ := parseTime(trade.IngestedAt)
		blockTime, _ := parseTime(trade.BlockTime)
		if ingestedAt.Before(blockTime) {
			issue := Issue{Row: line, EventID: trade.EventID, Code: "ingested_before_block", Message: "ingested_at is earlier than block_time", Disposition: "quarantine"}
			addIssue(&report, issue)
			report.Quarantined++
			report.QuarantineRecords = append(report.QuarantineRecords, RejectedRecord{Row: line, EventID: trade.EventID, Raw: rawRow, Issues: []Issue{issue}})
			continue
		}

		key := fmt.Sprintf("%s|%s|%s|%s|%d", trade.TxHash, trade.BlockTime, trade.Wallet, trade.Side, trade.Amount)
		if _, exists := seen[key]; exists {
			issue := Issue{Row: line, EventID: trade.EventID, Code: "duplicate_trade", Message: "trade matches an earlier tx_hash, block_time, wallet, side, and amount", Disposition: "skip"}
			addIssue(&report, issue)
			report.SkippedRecords = append(report.SkippedRecords, RejectedRecord{Row: line, EventID: trade.EventID, Raw: rawRow, Issues: []Issue{issue}})
			continue
		}
		seen[key] = struct{}{}
		report.Accepted = append(report.Accepted, trade)
	}
	return report, nil
}

func parseTime(value string) (time.Time, error) {
	return time.Parse("15:04:05", value)
}

func addIssue(report *Report, issue Issue) {
	report.Issues = append(report.Issues, issue)
	if issue.Disposition == "skip" {
		report.Skipped++
	}
}
