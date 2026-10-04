package main

import (
	"encoding/json"
	"io"
	"math/big"
)

type ReportOptions struct {
	InputPath    string
	AcceptedPath string
	RejectedPath string
}

type validationReport struct {
	SchemaVersion int            `json:"schema_version"`
	Input         string         `json:"input"`
	Summary       reportSummary  `json:"summary"`
	IssueCounts   map[string]int `json:"issue_counts"`
	Amounts       reportAmounts  `json:"amounts"`
	Outputs       reportOutputs  `json:"outputs"`
}

type reportSummary struct {
	InputRows     int     `json:"input_rows"`
	AcceptedRows  int     `json:"accepted_rows"`
	RejectedRows  int     `json:"rejected_rows"`
	RejectionRate float64 `json:"rejection_rate"`
}

type reportAmounts struct {
	ParseableInput    string `json:"parseable_input"`
	Accepted          string `json:"accepted"`
	RejectedParseable string `json:"rejected_parseable"`
}

type reportOutputs struct {
	Accepted   string `json:"accepted"`
	DeadLetter string `json:"dead_letter"`
}

func WriteReport(w io.Writer, result Result, options ReportOptions) error {
	issueCounts := make(map[string]int)
	acceptedAmount := new(big.Int)
	rejectedAmount := new(big.Int)
	for _, event := range result.Accepted {
		acceptedAmount.Add(acceptedAmount, big.NewInt(event.Amount))
	}
	for _, rejection := range result.Rejected {
		for _, issue := range rejection.Issues {
			issueCounts[issue.Code]++
		}
		if rejection.Event.Amount > 0 {
			rejectedAmount.Add(rejectedAmount, big.NewInt(rejection.Event.Amount))
		}
	}

	inputRows := len(result.Accepted) + len(result.Rejected)
	rejectionRate := 0.0
	if inputRows > 0 {
		rejectionRate = float64(len(result.Rejected)) / float64(inputRows)
	}
	parseableInput := new(big.Int).Add(new(big.Int).Set(acceptedAmount), rejectedAmount)

	report := validationReport{
		SchemaVersion: 1,
		Input:         options.InputPath,
		Summary: reportSummary{
			InputRows:     inputRows,
			AcceptedRows:  len(result.Accepted),
			RejectedRows:  len(result.Rejected),
			RejectionRate: rejectionRate,
		},
		IssueCounts: issueCounts,
		Amounts: reportAmounts{
			ParseableInput:    parseableInput.String(),
			Accepted:          acceptedAmount.String(),
			RejectedParseable: rejectedAmount.String(),
		},
		Outputs: reportOutputs{
			Accepted:   options.AcceptedPath,
			DeadLetter: options.RejectedPath,
		},
	}

	encoder := json.NewEncoder(w)
	encoder.SetIndent("", "  ")
	return encoder.Encode(report)
}
