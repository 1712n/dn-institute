package pipeline

import (
	"bytes"
	"encoding/csv"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"trade_feed_validator/models"
	"trade_feed_validator/validator"
)

var Columns = []string{"event_id", "tx_hash", "block_time", "wallet", "side", "amount", "ingested_at"}

// Rejected is a row sent to the dead-letter queue.
type Rejected struct {
	Line    int
	Raw     []string
	RawLine string // original text of the row, kept even when it is not valid CSV
	Errors  []models.ValidationError
}

func (r Rejected) EventID() string {
	if len(r.Raw) > 0 {
		return r.Raw[0]
	}
	return ""
}

type Result struct {
	Clean      []models.TradeEvent
	DeadLetter []Rejected
	RawVolume  int64 // sum of amount over every parseable row, i.e. what the old pipeline would load
}

func (r *Result) CleanVolume() int64 {
	var total int64
	for _, e := range r.Clean {
		total += e.Amount
	}
	return total
}

// ErrFeedDateRequired stops the run instead of inventing a calendar day for
// time-only timestamps.
var ErrFeedDateRequired = errors.New("feed has time-only timestamps but no feed date was given (use -date YYYY-MM-DD)")

type Pipeline struct {
	// FeedDate is the UTC day the feed belongs to. Time-only values (HH:MM:SS)
	// are anchored to it; if it is zero, such values stop the run.
	FeedDate  time.Time
	validator *validator.Validator
}

func NewPipeline(feedDate time.Time) *Pipeline {
	p := &Pipeline{validator: validator.NewValidator()}
	if !feedDate.IsZero() {
		p.FeedDate = time.Date(feedDate.Year(), feedDate.Month(), feedDate.Day(), 0, 0, 0, 0, time.UTC)
	}
	return p
}

func (p *Pipeline) Process(r io.Reader) (*Result, error) {
	capture := &rowCapture{r: r}
	reader := csv.NewReader(capture)
	reader.FieldsPerRecord = -1
	reader.TrimLeadingSpace = true

	header, err := reader.Read()
	if err != nil {
		return nil, fmt.Errorf("failed to read header: %w", err)
	}
	capture.take(reader.InputOffset())
	index, err := columnIndex(header)
	if err != nil {
		return nil, err
	}

	result := &Result{}
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		rawLine := capture.take(reader.InputOffset())
		var parseErr *csv.ParseError
		if errors.As(err, &parseErr) {
			raw := ordered(record, index)
			result.DeadLetter = append(result.DeadLetter, Rejected{Line: parseErr.StartLine, Raw: raw, RawLine: rawLine, Errors: []models.ValidationError{{
				EventID: nullable(strings.TrimSpace(raw[0])),
				Code:    models.CodeMalformedRow,
				Field:   "row",
				Reason:  fmt.Sprintf("invalid CSV: %v", parseErr.Err),
			}}})
			continue
		}
		if err != nil {
			return nil, fmt.Errorf("failed to read record: %w", err)
		}

		line, _ := reader.FieldPos(0)
		raw := ordered(record, index)
		event, errs, err := p.parseRecord(record, index, len(header))
		if err != nil {
			return nil, fmt.Errorf("line %d: %w", line, err)
		}
		if len(errs) == 0 {
			result.RawVolume += event.Amount
			errs = p.validator.Validate(event)
		}

		if len(errs) > 0 {
			result.DeadLetter = append(result.DeadLetter, Rejected{Line: line, Raw: raw, RawLine: rawLine, Errors: errs})
			continue
		}
		result.Clean = append(result.Clean, event)
	}
	return result, nil
}

// rowCapture keeps the bytes the CSV reader has pulled from the input, so the
// original text of each row can be cut out using csv.Reader.InputOffset.
type rowCapture struct {
	r      io.Reader
	buf    bytes.Buffer
	offset int64 // input offset of the first byte in buf
}

func (c *rowCapture) Read(p []byte) (int, error) {
	n, err := c.r.Read(p)
	c.buf.Write(p[:n])
	return n, err
}

// take returns the input text up to the end offset and drops it from the buffer.
func (c *rowCapture) take(end int64) string {
	n := int(end - c.offset)
	if n < 0 {
		n = 0
	}
	if n > c.buf.Len() {
		n = c.buf.Len()
	}
	c.offset += int64(n)
	return strings.Trim(string(c.buf.Next(n)), "\r\n")
}

func (p *Pipeline) ProcessFile(filename string) (*Result, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	return p.Process(file)
}

func columnIndex(header []string) (map[string]int, error) {
	index := make(map[string]int, len(header))
	for i, name := range header {
		if i == 0 {
			name = strings.TrimPrefix(name, "\ufeff")
		}
		key := strings.ToLower(strings.TrimSpace(name))
		if _, dup := index[key]; dup {
			return nil, fmt.Errorf("header has duplicate column %q", key)
		}
		index[key] = i
	}
	var missing []string
	for _, col := range Columns {
		if _, ok := index[col]; !ok {
			missing = append(missing, col)
		}
	}
	if len(missing) > 0 {
		return nil, fmt.Errorf("header is missing columns: %s", strings.Join(missing, ", "))
	}
	return index, nil
}

func ordered(record []string, index map[string]int) []string {
	out := make([]string, len(Columns))
	for i, col := range Columns {
		if j := index[col]; j < len(record) {
			out[i] = record[j]
		}
	}
	return out
}

// parseRecord returns row-level problems as validation errors; a non-nil error
// means the whole run must stop.
func (p *Pipeline) parseRecord(record []string, index map[string]int, width int) (models.TradeEvent, []models.ValidationError, error) {
	get := func(col string) string { return strings.TrimSpace(record[index[col]]) }
	eventID := ""
	if index["event_id"] < len(record) {
		eventID = nullable(get("event_id"))
	}

	if len(record) != width {
		return models.TradeEvent{}, []models.ValidationError{{
			EventID: eventID,
			Code:    models.CodeMalformedRow,
			Field:   "row",
			Reason:  fmt.Sprintf("row has %d fields, header has %d", len(record), width),
		}}, nil
	}

	var errs []models.ValidationError
	fail := func(code models.Code, field, reason string) {
		errs = append(errs, models.ValidationError{EventID: eventID, Code: code, Field: field, Reason: reason})
	}

	blockTime, err := p.parseTime(get("block_time"))
	if errors.Is(err, ErrFeedDateRequired) {
		return models.TradeEvent{}, nil, err
	} else if err != nil {
		fail(models.CodeInvalidTimestamp, "block_time", err.Error())
	}
	ingestedAt, err := p.parseTime(get("ingested_at"))
	if errors.Is(err, ErrFeedDateRequired) {
		return models.TradeEvent{}, nil, err
	} else if err != nil {
		fail(models.CodeInvalidTimestamp, "ingested_at", err.Error())
	}

	var amount int64
	if s := get("amount"); isNull(s) {
		fail(models.CodeInvalidAmount, "amount", "missing or null value")
	} else if amount, err = strconv.ParseInt(s, 10, 64); err != nil {
		fail(models.CodeInvalidAmount, "amount", fmt.Sprintf("not an integer: %q", s))
	}

	event := models.TradeEvent{
		EventID:    eventID,
		TxHash:     nullable(get("tx_hash")),
		BlockTime:  blockTime,
		Wallet:     nullable(get("wallet")),
		Side:       strings.ToUpper(nullable(get("side"))),
		Amount:     amount,
		IngestedAt: ingestedAt,
	}
	return event, errs, nil
}

// parseTime accepts a full timestamp or a time of day (HH:MM:SS). Null or empty values return the zero time.
func (p *Pipeline) parseTime(s string) (time.Time, error) {
	if isNull(s) {
		return time.Time{}, nil
	}
	if t, err := time.Parse(time.RFC3339, s); err == nil {
		return t.UTC(), nil
	}
	t, err := time.Parse("15:04:05", s)
	if err != nil {
		return time.Time{}, fmt.Errorf("cannot parse %q as HH:MM:SS or RFC 3339", s)
	}
	if p.FeedDate.IsZero() {
		return time.Time{}, ErrFeedDateRequired
	}
	return p.FeedDate.Add(time.Duration(t.Hour())*time.Hour +
		time.Duration(t.Minute())*time.Minute +
		time.Duration(t.Second())*time.Second), nil
}

func isNull(s string) bool {
	return s == "" || strings.EqualFold(s, "null")
}

func nullable(s string) string {
	if isNull(s) {
		return ""
	}
	return s
}

func WriteClean(w io.Writer, events []models.TradeEvent) error {
	cw := csv.NewWriter(w)
	if err := cw.Write(Columns); err != nil {
		return err
	}
	for _, e := range events {
		if err := cw.Write([]string{
			e.EventID,
			e.TxHash,
			e.BlockTime.UTC().Format(time.RFC3339),
			e.Wallet,
			e.Side,
			strconv.FormatInt(e.Amount, 10),
			e.IngestedAt.UTC().Format(time.RFC3339),
		}); err != nil {
			return err
		}
	}
	cw.Flush()
	return cw.Error()
}

func WriteDeadLetter(w io.Writer, rejected []Rejected) error {
	cw := csv.NewWriter(w)
	if err := cw.Write(append(append([]string{"line"}, Columns...), "error_codes", "error_details", "raw_line")); err != nil {
		return err
	}
	for _, r := range rejected {
		codes := make([]string, len(r.Errors))
		details := make([]string, len(r.Errors))
		for i, e := range r.Errors {
			codes[i] = string(e.Code)
			details[i] = e.Field + ": " + e.Reason
		}
		row := append([]string{strconv.Itoa(r.Line)}, r.Raw...)
		row = append(row, strings.Join(codes, ";"), strings.Join(details, "; "), r.RawLine)
		if err := cw.Write(row); err != nil {
			return err
		}
	}
	cw.Flush()
	return cw.Error()
}

// writes clean.csv and dead_letter.csv into dir output.
// Each file is written to a temporary file and renamed into place only after
// both were written, so a failed write never leaves a partial file. The pair
// is not published atomically; concurrent runs must use different -out dirs.
func WriteOutputs(dir string, result *Result) error {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	outputs := []struct {
		name  string
		write func(io.Writer) error
	}{
		{"clean.csv", func(w io.Writer) error { return WriteClean(w, result.Clean) }},
		{"dead_letter.csv", func(w io.Writer) error { return WriteDeadLetter(w, result.DeadLetter) }},
	}

	tmpPaths := make([]string, len(outputs))
	defer func() {
		for _, p := range tmpPaths {
			if p != "" {
				os.Remove(p)
			}
		}
	}()

	for i, out := range outputs {
		p, err := writeTemp(dir, out.name, out.write)
		if err != nil {
			return fmt.Errorf("writing %s: %w", out.name, err)
		}
		tmpPaths[i] = p
	}
	for i, out := range outputs {
		if err := os.Rename(tmpPaths[i], filepath.Join(dir, out.name)); err != nil {
			return fmt.Errorf("publishing %s: %w", out.name, err)
		}
		tmpPaths[i] = ""
	}
	return nil
}

func writeTemp(dir, name string, write func(io.Writer) error) (string, error) {
	f, err := os.CreateTemp(dir, "."+name+".tmp-*")
	if err != nil {
		return "", err
	}
	if err := f.Chmod(0o644); err != nil {
		f.Close()
		os.Remove(f.Name())
		return "", err
	}
	if err := write(f); err != nil {
		f.Close()
		os.Remove(f.Name())
		return "", err
	}
	if err := f.Close(); err != nil {
		os.Remove(f.Name())
		return "", err
	}
	return f.Name(), nil
}
