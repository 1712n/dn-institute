package main

import (
	"os"
	"slices"
	"strings"
	"testing"
)

func TestValidate(t *testing.T) {
	sampleFeed, err := os.ReadFile("sample_feed.csv")
	if err != nil {
		t.Fatal(err)
	}

	tests := []struct {
		name         string
		feed         string
		wantAccepted []string
		wantRejected map[string][]string
	}{
		{
			name:         "sample feed",
			feed:         string(sampleFeed),
			wantAccepted: []string{"evt_001", "evt_002", "evt_004", "evt_006"},
			wantRejected: map[string][]string{
				"evt_003": {"duplicate_trade"},
				"evt_005": {"missing_block_time"},
				"evt_007": {"duplicate_trade"},
				"evt_008": {"block_time_after_ingested_at"},
			},
		},
		{
			name: "same fields in different transactions",
			feed: `event_id,tx_hash,block_time,wallet,side,amount,ingested_at
evt_001,0xaa1,09:14:02,0xD4,BUY,120000,09:14:05
evt_002,0xaa2,09:41:20,0xD4,BUY,120000,09:41:23
`,
			wantAccepted: []string{"evt_001", "evt_002"},
		},
		{
			name: "arrival order differs from block order",
			feed: `event_id,tx_hash,block_time,wallet,side,amount,ingested_at
later,0xaa2,10:00:00,0xD4,BUY,1,10:00:01
earlier,0xaa1,09:00:00,0xD4,BUY,1,09:00:01
`,
			wantAccepted: []string{"earlier", "later"},
		},
		{
			name: "multiple invalid fields",
			feed: `event_id,tx_hash,block_time,wallet,side,amount,ingested_at
bad,0xaa1,not-a-time,0xD4,HOLD,-1,also-not-a-time
`,
			wantRejected: map[string][]string{
				"bad": {"invalid_side", "invalid_amount", "invalid_block_time", "invalid_ingested_at"},
			},
		},
		{
			name: "duplicate event id",
			feed: `event_id,tx_hash,block_time,wallet,side,amount,ingested_at
evt,0xaa1,09:00:00,0xD4,BUY,1,09:00:01
evt,0xaa2,09:01:00,0xD4,BUY,1,09:01:01
`,
			wantAccepted: []string{"evt"},
			wantRejected: map[string][]string{
				"evt": {"duplicate_event_id"},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := Validate(strings.NewReader(tt.feed))
			if err != nil {
				t.Fatal(err)
			}

			if got := eventIDs(result.Accepted); !slices.Equal(got, tt.wantAccepted) {
				t.Errorf("accepted IDs = %v, want %v", got, tt.wantAccepted)
			}
			if len(result.Rejected) != len(tt.wantRejected) {
				t.Fatalf("rejected count = %d, want %d", len(result.Rejected), len(tt.wantRejected))
			}

			seen := make(map[string]bool, len(result.Rejected))
			for _, rejection := range result.Rejected {
				id := rejection.Event.EventID
				wantCodes, exists := tt.wantRejected[id]
				if !exists {
					t.Errorf("unexpected rejection %q: %v", id, rejection.Issues)
					continue
				}
				seen[id] = true
				if len(rejection.Issues) != len(wantCodes) {
					t.Errorf("%s has %d issues, want %d: %v", id, len(rejection.Issues), len(wantCodes), rejection.Issues)
				}
				for _, code := range wantCodes {
					if !hasIssue(rejection.Issues, code) {
						t.Errorf("%s issues = %v, want code %s", id, rejection.Issues, code)
					}
				}
			}
			for id := range tt.wantRejected {
				if !seen[id] {
					t.Errorf("expected rejection %q was not returned", id)
				}
			}
		})
	}
}

func TestValidateRejectsInvalidCSVSchema(t *testing.T) {
	tests := []struct {
		name    string
		feed    string
		wantErr string
	}{
		{
			name:    "missing required column",
			feed:    "event_id,tx_hash,block_time,wallet,side,amount\n",
			wantErr: `missing required CSV column "ingested_at"`,
		},
		{
			name:    "duplicate column",
			feed:    "event_id,tx_hash,block_time,wallet,side,amount,ingested_at,event_id\n",
			wantErr: `duplicate CSV column "event_id"`,
		},
		{
			name:    "malformed CSV",
			feed:    "event_id,tx_hash,block_time,wallet,side,amount,ingested_at\n\"unterminated",
			wantErr: "read CSV row 2",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := Validate(strings.NewReader(tt.feed))
			if err == nil || !strings.Contains(err.Error(), tt.wantErr) {
				t.Fatalf("Validate() error = %v, want error containing %q", err, tt.wantErr)
			}
		})
	}
}

func eventIDs(events []Event) []string {
	ids := make([]string, len(events))
	for i, event := range events {
		ids[i] = event.EventID
	}
	return ids
}

func hasIssue(issues []Issue, code string) bool {
	for _, issue := range issues {
		if issue.Code == code {
			return true
		}
	}
	return false
}
