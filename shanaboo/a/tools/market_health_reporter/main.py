#!/usr/bin/env python3 🌰
"""Main entry point for Market Health Reporter."""

import argparse
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG functionality")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.no_rag:
        config["rag_enabled"] = False
    
    # Initialize reporter
    reporter = MarketHealthReporter(config)
    
    anomalies = reporter.detect_anomalies(data)
    
    if not anomalies:
        print(f"No significant anomalies detected for {args.exchange} 🌰")
        return
    
    # Generate report