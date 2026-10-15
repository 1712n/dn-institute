package models

import (
	"time"
)

const (
	SideBuy  = "BUY"
	SideSell = "SELL"
)

type TradeEvent struct {
	EventID    string
	TxHash     string
	BlockTime  time.Time
	Wallet     string
	Side       string
	Amount     int64
	IngestedAt time.Time
}

type TradeKey struct {
	TxHash    string
	Wallet    string
	Side      string
	Amount    int64
	BlockTime time.Time
}

func (e TradeEvent) Key() TradeKey {
	return TradeKey{
		TxHash:    e.TxHash,
		Wallet:    e.Wallet,
		Side:      e.Side,
		Amount:    e.Amount,
		BlockTime: e.BlockTime.UTC(),
	}
}

type Code string

const (
	CodeMalformedRow         Code = "malformed_row"
	CodeMissingField         Code = "missing_field"
	CodeInvalidTimestamp     Code = "invalid_timestamp"
	CodeMissingBlockTime     Code = "missing_block_time"
	CodeInvalidSide          Code = "invalid_side"
	CodeInvalidAmount        Code = "invalid_amount"
	CodeBlockTimeAfterIngest Code = "block_time_after_ingested_at"
	CodeDuplicateEventID     Code = "duplicate_event_id"
	CodeExactDuplicate       Code = "exact_duplicate"
	CodeRedeliveredDuplicate Code = "redelivered_duplicate"
)

type ValidationError struct {
	EventID string
	Code    Code
	Field   string
	Reason  string
}

func (e ValidationError) Error() string {
	return "event " + e.EventID + ": " + string(e.Code) + " (" + e.Field + ") - " + e.Reason
}
