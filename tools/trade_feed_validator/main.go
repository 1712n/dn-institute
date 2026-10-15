package main

import (
	"flag"
	"fmt"
	"os"
	"sort"
	"time"

	"trade_feed_validator/models"
	"trade_feed_validator/pipeline"
)

func main() {
	dateFlag := flag.String("date", "", "UTC date (YYYY-MM-DD) of the feed; required when timestamps are times of day only")
	outDir := flag.String("out", "output", "directory for clean.csv and dead_letter.csv")
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [-date YYYY-MM-DD] [-out DIR] [feed.csv]\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	filename := "sample_feed.csv"
	if flag.NArg() > 0 {
		filename = flag.Arg(0)
	}

	var feedDate time.Time
	if *dateFlag != "" {
		d, err := time.Parse("2006-01-02", *dateFlag)
		if err != nil {
			fmt.Fprintf(os.Stderr, "invalid -date %q: %v\n", *dateFlag, err)
			os.Exit(2)
		}
		feedDate = d
	}

	fmt.Printf("Begin trade feed from: %s\n\n", filename)

	result, err := pipeline.NewPipeline(feedDate).ProcessFile(filename)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Pipeline error: %v\n", err)
		os.Exit(1)
	}
	if err := pipeline.WriteOutputs(*outDir, result); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to write outputs: %v\n", err)
		os.Exit(1)
	}

	printReport(result, *outDir)
}

func printReport(result *pipeline.Result, outDir string) {
	for _, e := range result.Clean {
		fmt.Printf("ACCEPTED  %s\n", e.EventID)
	}
	for _, r := range result.DeadLetter {
		for _, e := range r.Errors {
			fmt.Printf("REJECTED  %s  line %d  %s (%s): %s\n", r.EventID(), r.Line, e.Code, e.Field, e.Reason)
		}
	}

	counts := map[models.Code]int{}
	for _, r := range result.DeadLetter {
		for _, e := range r.Errors {
			counts[e.Code]++
		}
	}
	codes := make([]string, 0, len(counts))
	for c := range counts {
		codes = append(codes, string(c))
	}
	sort.Strings(codes)

	fmt.Printf("\nProcessing complete:\n")
	fmt.Printf("  Accepted events:      %d\n", len(result.Clean))
	fmt.Printf("  Dead-lettered events: %d\n", len(result.DeadLetter))
	for _, c := range codes {
		fmt.Printf("    %-30s %d\n", c, counts[models.Code(c)])
	}
	fmt.Printf("  Volume if loaded as-is: %d\n", result.RawVolume)
	fmt.Printf("  Volume after validation: %d\n", result.CleanVolume())
	fmt.Printf("\nWrote %s/clean.csv and %s/dead_letter.csv\n", outDir, outDir)
}
