#!/usr/bin/env python3
"""
Market Health Reporter - Automated report generation with RAG enhancement 🌰
Enhanced with Retrieval Augmented Generation for better context and interpretation
"""

import argparse
from datetime import datetime, timedelta
from market_health_api import MarketHealthAPI
from report_generator import ReportGenerator
from rag_enhancer import RAGEnhancer


def parse_args():
        default="./reports",
        help="Directory to save reports (default: ./reports)"
    )
    parser.add_argument(
        "--enable-rag",
        action="store_true",
        default=True,
        help="Enable RAG functionality for enhanced context (default: true)"
    )
    return parser.parse_args()


        print("🌰 Initializing Market Health Reporter...")
        api = MarketHealthAPI()
        generator = ReportGenerator(api)
        
        rag_enhancer = None
        if args.enable_rag:
            print("🌰 Initializing RAG Enhancer...")
            rag_enhancer = RAGEnhancer()

        # Fetch data
        print(f"🌰 Fetching data for {args.exchange} on {args.date}...")

        # Generate report
        print("🌰 Generating report...")
        
        if rag_enhancer:
            enhanced_data = rag_enhancer.enhance_report_data(data, args.exchange, args.date)
            report_content = generator.generate_report(enhanced_data, args.exchange, args.date)
        else:
            report_content = generator.generate_report(data, args.exchange, args.date)

        # Save report
        output_dir = Path(args.output_dir)