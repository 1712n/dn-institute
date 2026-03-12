import argparse
import os
from datetime import datetime, timedelta
from rag_context import RAGContextProvider

from market_health_api import MarketHealthAPI
from report_generator import ReportGenerator
    parser.add_argument('--exchange', required=True, help='Exchange name (e.g., binance, coinbase)')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--output', default='report.md', help='Output file name')
    parser.add_argument('--use-rag', action='store_true', help='Enable RAG functionality for enhanced context')
    
    args = parser.parse_args()
    
    api = MarketHealthAPI()
    generator = ReportGenerator()
    
    # Initialize RAG provider if enabled 🌰
    rag_provider = None
    if args.use_rag:
        rag_provider = RAGContextProvider()
    
    # Fetch market health data 📊
    try:
        date_obj = datetime.strptime(args.date, '%Y-%m-%d').date()
        data = api.get_exchange_metrics(args.exchange, date_obj)
        print(f"Error fetching data: {e}")
        return
    
    # Generate report with RAG context if available 📝
    try:
        report = generator.generate_report(
            exchange=args.exchange,