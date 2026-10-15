package validator

import (
	"fmt"
	"time"

	"trade_feed_validator/models"
)

// Validator checks events one by one in arrival order. It is stateful: it
// remembers accepted events to detect duplicates. Rejected events are never
// remembered, so a corrected version of a rejected event (e.g. evt_005 after
// block_time is backfilled) can still be accepted later.
type Validator struct {
	acceptedByKey    map[models.TradeKey]models.TradeEvent
	acceptedEventIDs map[string]bool
}

func NewValidator() *Validator {
	return &Validator{
		acceptedByKey:    make(map[models.TradeKey]models.TradeEvent),
		acceptedEventIDs: make(map[string]bool),
	}
}

// Validate returns all problems found for the event.
func (v *Validator) Validate(event models.TradeEvent) []models.ValidationError {
	errs := CheckFields(event)
	if len(errs) > 0 {
		return errs
	}

	errs = v.checkDuplicates(event)
	if len(errs) > 0 {
		return errs
	}

	v.acceptedByKey[event.Key()] = event
	v.acceptedEventIDs[event.EventID] = true
	return nil
}

// CheckFields runs checks that need only the event itself.
func CheckFields(event models.TradeEvent) []models.ValidationError {
	var errs []models.ValidationError
	add := func(code models.Code, field, reason string) {
		errs = append(errs, models.ValidationError{EventID: event.EventID, Code: code, Field: field, Reason: reason})
	}

	if event.EventID == "" {
		add(models.CodeMissingField, "event_id", "missing or empty value")
	}
	if event.TxHash == "" {
		add(models.CodeMissingField, "tx_hash", "missing or empty value")
	}
	if event.Wallet == "" {
		add(models.CodeMissingField, "wallet", "missing or empty value")
	}
	if event.BlockTime.IsZero() {
		add(models.CodeMissingBlockTime, "block_time", "missing or null value")
	}
	if event.IngestedAt.IsZero() {
		add(models.CodeMissingField, "ingested_at", "missing or null value")
	}
	if event.Side != models.SideBuy && event.Side != models.SideSell {
		add(models.CodeInvalidSide, "side", fmt.Sprintf("expected BUY or SELL, got %q", event.Side))
	}
	if event.Amount <= 0 {
		add(models.CodeInvalidAmount, "amount", fmt.Sprintf("must be positive, got %d", event.Amount))
	}
	if !event.BlockTime.IsZero() && !event.IngestedAt.IsZero() && event.BlockTime.After(event.IngestedAt) {
		add(models.CodeBlockTimeAfterIngest, "block_time",
			fmt.Sprintf("block_time %s is after ingested_at %s",
				event.BlockTime.UTC().Format(time.RFC3339), event.IngestedAt.UTC().Format(time.RFC3339)))
	}

	return errs
}

func (v *Validator) checkDuplicates(event models.TradeEvent) []models.ValidationError {
	if v.acceptedEventIDs[event.EventID] {
		return []models.ValidationError{{
			EventID: event.EventID,
			Code:    models.CodeDuplicateEventID,
			Field:   "event_id",
			Reason:  "event_id was already accepted",
		}}
	}

	original, seen := v.acceptedByKey[event.Key()]
	if !seen {
		return nil
	}

	if original.IngestedAt.Equal(event.IngestedAt) {
		return []models.ValidationError{{
			EventID: event.EventID,
			Code:    models.CodeExactDuplicate,
			Field:   "tx_hash",
			Reason:  fmt.Sprintf("identical copy of %s (same trade, same ingested_at)", original.EventID),
		}}
	}
	return []models.ValidationError{{
		EventID: event.EventID,
		Code:    models.CodeRedeliveredDuplicate,
		Field:   "tx_hash",
		Reason: fmt.Sprintf("same trade as %s delivered again at %s",
			original.EventID, event.IngestedAt.UTC().Format(time.RFC3339)),
	}}
}
