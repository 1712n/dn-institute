import argparse
import os
from datetime import datetime, timedelta
from rag_context import RAGContextRetriever

from market_health_client import MarketHealthClient
from report_generator import ReportGenerator
    parser.add_argument('--exchange', required=True, help='Exchange name (e.g., binance)')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--output', default='report.md', help='Output file name')
    parser.add_argument('--use-rag', action='store_true', help='Enable RAG for enhanced context')
    
    args = parser.parse_args()
    
    client = MarketHealthClient(api_key)
    generator = ReportGenerator()
    
    rag_retriever = None
    if args.use_rag:
        print("🌰 Enabling RAG context retrieval for enhanced market analysis...")
        rag_retriever = RAGContextRetriever()
    
    report = generator.generate_report(client, args.exchange, date, rag_retriever)
    
    with open(args.output, 'w') as f:
        f.write(report)