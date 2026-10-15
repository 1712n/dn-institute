package validator

import (
	"testing"
	"time"

	"trade_feed_validator/models"
)

func at(hms string) time.Time {
	t, err := time.Parse("15:04:05", hms)
	if err != nil {
		panic(err)
	}
	return time.Date(2026, 1, 1, t.Hour(), t.Minute(), t.Second(), 0, time.UTC)
}

func validEvent(id, tx string) models.TradeEvent {
	return models.TradeEvent{
		EventID:    id,
		TxHash:     tx,
		BlockTime:  at("09:41:20"),
		Wallet:     "0xD4",
		Side:       models.SideBuy,
		Amount:     120000,
		IngestedAt: at("09:41:23"),
	}
}

func codes(errs []models.ValidationError) []models.Code {
	out := make([]models.Code, len(errs))
	for i, e := range errs {
		out[i] = e.Code
	}
	return out
}

func assertCodes(t *testing.T, errs []models.ValidationError, want ...models.Code) {
	t.Helper()
	got := codes(errs)
	if len(got) != len(want) {
		t.Fatalf("got codes %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("got codes %v, want %v", got, want)
		}
	}
}

func TestValidEventIsAccepted(t *testing.T) {
	assertCodes(t, NewValidator().Validate(validEvent("evt_001", "0xaa1")))
}

// evt_005: block_time is null.
func TestMissingBlockTime(t *testing.T) {
	e := validEvent("evt_005", "0xaa4")
	e.BlockTime = time.Time{}
	assertCodes(t, NewValidator().Validate(e), models.CodeMissingBlockTime)
}

// evt_008: block_time 10:10:00 is after ingested_at 09:59:50.
func TestBlockTimeAfterIngestedAt(t *testing.T) {
	e := validEvent("evt_008", "0xaa6")
	e.BlockTime = at("10:10:00")
	e.IngestedAt = at("09:59:50")
	errs := NewValidator().Validate(e)
	assertCodes(t, errs, models.CodeBlockTimeAfterIngest)
	if want := "block_time 2026-01-01T10:10:00Z is after ingested_at 2026-01-01T09:59:50Z"; errs[0].Reason != want {
		t.Errorf("reason = %q, want %q", errs[0].Reason, want)
	}
}

func TestBlockTimeEqualToIngestedAtIsAccepted(t *testing.T) {
	e := validEvent("evt_x", "0xbb1")
	e.IngestedAt = e.BlockTime
	assertCodes(t, NewValidator().Validate(e))
}

// evt_002 / evt_003: same trade delivered twice, different ingested_at.
func TestRedeliveredDuplicate(t *testing.T) {
	v := NewValidator()
	first := validEvent("evt_002", "0xaa2")
	second := validEvent("evt_003", "0xaa2")
	second.IngestedAt = at("09:44:01")

	assertCodes(t, v.Validate(first))
	assertCodes(t, v.Validate(second), models.CodeRedeliveredDuplicate)
}

// evt_006 / evt_007: byte-for-byte copy apart from event_id.
func TestExactDuplicate(t *testing.T) {
	v := NewValidator()
	first := validEvent("evt_006", "0xaa5")
	second := validEvent("evt_007", "0xaa5")

	assertCodes(t, v.Validate(first))
	assertCodes(t, v.Validate(second), models.CodeExactDuplicate)
}

func TestSameEventIDTwiceIsRejected(t *testing.T) {
	v := NewValidator()
	assertCodes(t, v.Validate(validEvent("evt_001", "0xaa1")))
	assertCodes(t, v.Validate(validEvent("evt_001", "0xccc")), models.CodeDuplicateEventID)
}

// Two different trades inside one transaction (e.g. a multi-hop swap) share a
// tx_hash and must both be kept.
func TestDifferentTradesInSameTransactionAreKept(t *testing.T) {
	v := NewValidator()
	buy := validEvent("evt_a", "0xmulti")
	sell := validEvent("evt_b", "0xmulti")
	sell.Side = models.SideSell
	sell.Amount = 5000

	assertCodes(t, v.Validate(buy))
	assertCodes(t, v.Validate(sell))
}

// Same wallet, side and amount but a different transaction is a separate trade
// (evt_001 vs evt_002 in the sample).
func TestSameContentDifferentTxIsKept(t *testing.T) {
	v := NewValidator()
	first := validEvent("evt_001", "0xaa1")
	first.BlockTime = at("09:14:02")
	first.IngestedAt = at("09:14:05")

	assertCodes(t, v.Validate(first))
	assertCodes(t, v.Validate(validEvent("evt_002", "0xaa2")))
}

// A rejected event must not block its corrected replay from the dead-letter queue.
func TestRejectedEventDoesNotBlockBackfilledReplay(t *testing.T) {
	v := NewValidator()
	broken := validEvent("evt_005", "0xaa4")
	broken.BlockTime = time.Time{}
	assertCodes(t, v.Validate(broken), models.CodeMissingBlockTime)

	backfilled := validEvent("evt_005", "0xaa4")
	assertCodes(t, v.Validate(backfilled))
}

func TestFieldChecks(t *testing.T) {
	tests := []struct {
		name   string
		modify func(*models.TradeEvent)
		want   []models.Code
	}{
		{"missing tx_hash", func(e *models.TradeEvent) { e.TxHash = "" }, []models.Code{models.CodeMissingField}},
		{"missing wallet", func(e *models.TradeEvent) { e.Wallet = "" }, []models.Code{models.CodeMissingField}},
		{"missing event_id", func(e *models.TradeEvent) { e.EventID = "" }, []models.Code{models.CodeMissingField}},
		{"missing ingested_at", func(e *models.TradeEvent) { e.IngestedAt = time.Time{} }, []models.Code{models.CodeMissingField}},
		{"unknown side", func(e *models.TradeEvent) { e.Side = "HOLD" }, []models.Code{models.CodeInvalidSide}},
		{"zero amount", func(e *models.TradeEvent) { e.Amount = 0 }, []models.Code{models.CodeInvalidAmount}},
		{"negative amount", func(e *models.TradeEvent) { e.Amount = -10 }, []models.Code{models.CodeInvalidAmount}},
		{"several problems at once", func(e *models.TradeEvent) {
			e.BlockTime = time.Time{}
			e.Side = ""
		}, []models.Code{models.CodeMissingBlockTime, models.CodeInvalidSide}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			e := validEvent("evt_x", "0xaa1")
			tt.modify(&e)
			assertCodes(t, CheckFields(e), tt.want...)
		})
	}
}
