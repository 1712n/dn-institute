package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/1712n/dn-institute/tools/trade_feed_validator/internal/validator"
)

func main() {
	filename := "sample_feed.csv"
	if len(os.Args) > 1 {
		filename = os.Args[1]
	}

	report, err := validator.ValidateFeed(filename)
	if err != nil {
		fmt.Fprintln(os.Stderr, "validation failed:", err)
		os.Exit(1)
	}

	if err := json.NewEncoder(os.Stdout).Encode(report); err != nil {
		fmt.Fprintln(os.Stderr, "write report:", err)
		os.Exit(1)
	}
}
