package main

import (
	"fmt"
	"os"
	"path/filepath"
)

const (
	validOutputName  = "valid_trades.csv"
	dlqOutputName    = "rejected_events.csv"
	reportOutputName = "validation_report.json"
)

func runPipeline(inputPath, outputDir string) (Result, error) {
	input, err := os.Open(inputPath)
	if err != nil {
		return Result{}, fmt.Errorf("open input: %w", err)
	}
	defer input.Close()

	result, err := Validate(input)
	if err != nil {
		return Result{}, err
	}

	if err := os.MkdirAll(outputDir, 0o755); err != nil {
		return Result{}, fmt.Errorf("create output directory: %w", err)
	}
	validPath := filepath.Join(outputDir, validOutputName)
	dlqPath := filepath.Join(outputDir, dlqOutputName)
	reportPath := filepath.Join(outputDir, reportOutputName)

	if err := writeAcceptedFile(validPath, result.Accepted); err != nil {
		return Result{}, fmt.Errorf("write valid output: %w", err)
	}
	if err := writeRejectedFile(dlqPath, result.Rejected); err != nil {
		return Result{}, fmt.Errorf("write DLQ output: %w", err)
	}
	if err := writeReportFile(reportPath, result, inputPath); err != nil {
		return Result{}, fmt.Errorf("write validation report: %w", err)
	}

	return result, nil
}

func writeAcceptedFile(path string, events []Event) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	writeErr := WriteAccepted(file, events)
	closeErr := file.Close()
	if writeErr != nil {
		return writeErr
	}
	return closeErr
}

func writeRejectedFile(path string, rejected []Rejection) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	writeErr := WriteRejected(file, rejected)
	closeErr := file.Close()
	if writeErr != nil {
		return writeErr
	}
	return closeErr
}

func writeReportFile(path string, result Result, inputPath string) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	writeErr := WriteReport(file, result, ReportOptions{
		InputPath:    inputPath,
		AcceptedPath: validOutputName,
		RejectedPath: dlqOutputName,
	})
	closeErr := file.Close()
	if writeErr != nil {
		return writeErr
	}
	return closeErr
}
