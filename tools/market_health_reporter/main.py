#!/usr/bin/env python3
"""
Market Health Reporter - Automated report generation for market health metrics with RAG 🌰
"""

import argparse
import os
from datetime import datetime, timedelta
from market_health_client import MarketHealthClient
from rag_context import RAGContextRetriever
from enhanced_report_generator import EnhancedReportGenerator
from report_generator import ReportGenerator


    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--model', choices=['gpt-4', 'claude-3-opus'], default='gpt-4', help='LLM model to use')
    parser.add_argument('--enable-rag', action='store_true', help='Enable RAG context retrieval')
    parser.add_argument('--max-articles', type=int, default=5, help='Maximum articles to retrieve per spike')
    parser.add_argument('--search-days', type=int, default=7, help='Days to search for relevant articles')
    
    args = parser.parse_args()
    
    client = MarketHealthClient(api_key=os.getenv('MARKET_HEALTH_API_KEY'))
    
    # Get spikes for the exchange and date
    print(f"Fetching spikes for {args.exchange} on {args.date}... 🌰")
    spikes = client.get_spikes(args.exchange, args.date)
    
    if not spikes:
        print("No spikes found for this date.")
        return
    
    # Initialize RAG retriever if enabled
    rag_retriever = None
    if args.enable_rag:
        print("Initializing RAG context retriever... 🌰")
        rag_retriever = RAGContextRetriever(
            max_articles=args.max_articles,
            search_days=args.search_days
        )
    
    # Generate enhanced report with RAG
    generator = EnhancedReportGenerator(model=args.model, rag_retriever=rag_retriever)
    report = generator.generate_enhanced_report(args.exchange, args.date, spikes)
    
    # Save report
    os.makedirs(args.output_dir, exist_ok=True)
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"Report saved to {filename} 🌰")


if __name__ == "__main__":