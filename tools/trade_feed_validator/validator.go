package main

import (
	"encoding/csv"
	"errors"
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"
	"time"
)

var requiredColumns = []string{
	"event_id", "tx_hash", "block_time", "wallet", "side", "amount", "ingested_at",
}

type Event struct {
	EventID       string
	TxHash        string
	BlockTimeRaw  string
	Wallet        string
	Side          string
	AmountRaw     string
	IngestedAtRaw string

	BlockTime  time.Time
	IngestedAt time.Time
	Amount     int64
	Row        int
}

type Issue struct {
	Code    string
	Message string
}

type Rejection struct {
	Event  Event
	Issues []Issue
}

type Result struct {
	Accepted []Event
	Rejected []Rejection
}

func Validate(r io.Reader) (Result, error) {
	cr := csv.NewReader(r)
	cr.TrimLeadingSpace = true
	header, err := cr.Read()
	if err != nil {
		return Result{}, fmt.Errorf("read CSV header: %w", err)
	}
	columns, err := indexColumns(header)
	if err != nil {
		return Result{}, err
	}

	var result Result
	seenEventIDs := make(map[string]string)
	seenTrades := make(map[string]string)

	for row := 2; ; row++ {
		record, readErr := cr.Read()
		if errors.Is(readErr, io.EOF) {
			break
		}
		if readErr != nil {
			return Result{}, fmt.Errorf("read CSV row %d: %w", row, readErr)
		}

		event := eventFromRecord(record, columns, row)
		issues := validateEvent(&event)
		if len(issues) == 0 {
			fingerprint := tradeFingerprint(event)
			if first, exists := seenEventIDs[event.EventID]; exists {
				issues = append(issues, Issue{
					Code:    "duplicate_event_id",
					Message: fmt.Sprintf("event_id already accepted as %s", first),
				})
			}
			if first, exists := seenTrades[fingerprint]; exists {
				issues = append(issues, Issue{
					Code:    "duplicate_trade",
					Message: fmt.Sprintf("same canonical trade already accepted as %s", first),
				})
			}
			if len(issues) == 0 {
				seenEventIDs[event.EventID] = event.EventID
				seenTrades[fingerprint] = event.EventID
			}
		}

		if len(issues) > 0 {
			result.Rejected = append(result.Rejected, Rejection{Event: event, Issues: issues})
			continue
		}
		result.Accepted = append(result.Accepted, event)
	}

	sort.SliceStable(result.Accepted, func(i, j int) bool {
		if result.Accepted[i].BlockTime.Equal(result.Accepted[j].BlockTime) {
			return result.Accepted[i].EventID < result.Accepted[j].EventID
		}
		return result.Accepted[i].BlockTime.Before(result.Accepted[j].BlockTime)
	})

	return result, nil
}

func indexColumns(header []string) (map[string]int, error) {
	columns := make(map[string]int, len(header))
	for i, name := range header {
		name = strings.TrimSpace(name)
		if _, exists := columns[name]; exists {
			return nil, fmt.Errorf("duplicate CSV column %q", name)
		}
		columns[name] = i
	}
	for _, name := range requiredColumns {
		if _, exists := columns[name]; !exists {
			return nil, fmt.Errorf("missing required CSV column %q", name)
		}
	}
	return columns, nil
}

func eventFromRecord(record []string, columns map[string]int, row int) Event {
	value := func(name string) string {
		i := columns[name]
		if i >= len(record) {
			return ""
		}
		return strings.TrimSpace(record[i])
	}
	return Event{
		EventID:       value("event_id"),
		TxHash:        value("tx_hash"),
		BlockTimeRaw:  value("block_time"),
		Wallet:        value("wallet"),
		Side:          strings.ToUpper(value("side")),
		AmountRaw:     value("amount"),
		IngestedAtRaw: value("ingested_at"),
		Row:           row,
	}
}

func validateEvent(event *Event) []Issue {
	var issues []Issue
	require := func(value, code, field string) {
		if value == "" {
			issues = append(issues, Issue{Code: code, Message: field + " is required"})
		}
	}
	require(event.EventID, "missing_event_id", "event_id")
	require(event.TxHash, "missing_tx_hash", "tx_hash")
	require(event.Wallet, "missing_wallet", "wallet")

	if event.Side != "BUY" && event.Side != "SELL" {
		issues = append(issues, Issue{Code: "invalid_side", Message: "side must be BUY or SELL"})
	}

	amount, err := strconv.ParseInt(event.AmountRaw, 10, 64)
	if err != nil || amount <= 0 {
		issues = append(issues, Issue{Code: "invalid_amount", Message: "amount must be a positive base-10 integer"})
	} else {
		event.Amount = amount
	}

	if event.BlockTimeRaw == "" {
		issues = append(issues, Issue{Code: "missing_block_time", Message: "block_time is required"})
	} else if event.BlockTime, err = parseUTCTime(event.BlockTimeRaw); err != nil {
		issues = append(issues, Issue{Code: "invalid_block_time", Message: err.Error()})
	}

	if event.IngestedAtRaw == "" {
		issues = append(issues, Issue{Code: "missing_ingested_at", Message: "ingested_at is required"})
	} else if event.IngestedAt, err = parseUTCTime(event.IngestedAtRaw); err != nil {
		issues = append(issues, Issue{Code: "invalid_ingested_at", Message: err.Error()})
	}

	if !event.BlockTime.IsZero() && !event.IngestedAt.IsZero() &&
		event.BlockTime.After(event.IngestedAt) {
		issues = append(issues, Issue{
			Code:    "block_time_after_ingested_at",
			Message: "block_time cannot be later than ingested_at",
		})
	}
	return issues
}

func parseUTCTime(value string) (time.Time, error) {
	for _, layout := range []string{time.RFC3339Nano, "15:04:05"} {
		if parsed, err := time.Parse(layout, value); err == nil {
			return parsed.UTC(), nil
		}
	}
	return time.Time{}, fmt.Errorf("%q is not RFC3339 or HH:MM:SS", value)
}

func tradeFingerprint(event Event) string {
	parts := []string{
		event.TxHash,
		event.BlockTime.Format(time.RFC3339Nano),
		event.Wallet,
		event.Side,
		strconv.FormatInt(event.Amount, 10),
	}
	return strings.Join(parts, "\x00")
}

func WriteAccepted(w io.Writer, events []Event) error {
	cw := csv.NewWriter(w)
	if err := cw.Write(requiredColumns); err != nil {
		return err
	}
	for _, event := range events {
		if err := cw.Write(eventRecord(event)); err != nil {
			return err
		}
	}
	cw.Flush()
	return cw.Error()
}

func WriteRejected(w io.Writer, rejected []Rejection) error {
	cw := csv.NewWriter(w)
	header := append(append([]string{}, requiredColumns...), "source_row", "issue_codes", "issue_details")
	if err := cw.Write(header); err != nil {
		return err
	}
	for _, rejection := range rejected {
		codes := make([]string, 0, len(rejection.Issues))
		details := make([]string, 0, len(rejection.Issues))
		for _, issue := range rejection.Issues {
			codes = append(codes, issue.Code)
			details = append(details, issue.Message)
		}
		record := append(eventRecord(rejection.Event), strconv.Itoa(rejection.Event.Row), strings.Join(codes, ";"), strings.Join(details, "; "))
		if err := cw.Write(record); err != nil {
			return err
		}
	}
	cw.Flush()
	return cw.Error()
}

func eventRecord(event Event) []string {
	return []string{
		event.EventID,
		event.TxHash,
		event.BlockTimeRaw,
		event.Wallet,
		event.Side,
		event.AmountRaw,
		event.IngestedAtRaw,
	}
}
