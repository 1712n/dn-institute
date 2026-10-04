package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	inputPath := flag.String("input", "sample_feed.csv", "input CSV path")
	outputDir := flag.String("output-dir", "output", "directory for validation outputs")
	flag.Parse()

	result, err := runPipeline(*inputPath, *outputDir)
	if err != nil {
		fmt.Fprintln(os.Stderr, "trade-feed-validator:", err)
		os.Exit(1)
	}

	fmt.Printf(
		"processed=%d accepted=%d rejected=%d output_dir=%s\n",
		len(result.Accepted)+len(result.Rejected),
		len(result.Accepted),
		len(result.Rejected),
		*outputDir,
	)
}
