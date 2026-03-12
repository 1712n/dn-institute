#!/usr/bin/env python3
"""
Market Health Reporter - Automated report generation for exchange metrics 🌰
Enhanced with RAG (Retrieval Augmented Generation) for superior context 🌰
"""

import argparse
from datetime import datetime, timedelta
from market_health_api import MarketHealthAPI
from report_generator import ReportGenerator
from rag_engine import RAGEngine


def parse_args():
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--model", default="gpt-4", help="AI model to use")
    parser.add_argument("--output-dir", default="./reports", help="Output directory")
    parser.add_argument("--use-rag", action="store_true", help="Enable RAG for enhanced context")
    return parser.parse_args()


    # Initialize components
    api = MarketHealthAPI()
    generator = ReportGenerator(model=args.model)
    rag_engine = RAGEngine() if args.use_rag else None

    # Fetch market health data
    print(f"Fetching data for {args.exchange} on {args.date}...")
    data = api.get_exchange_data(args.exchange, args.date)
        print("No data available for the specified date")
        return
    
    # Fetch additional context with RAG if enabled
    additional_context = ""
    if rag_engine:
        print("🔍 Gathering additional context via RAG...")
        additional_context = rag_engine.get_context(args.exchange, args.date, data)
    
    # Generate report
    print("🌰 Generating enhanced report with RAG context...")
    report = generator.generate_report(args.exchange, args.date, data, additional_context)
    
    # Save report
    os.makedirs(args.output_dir, exist_ok=True)