import argparse
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from market_health_api import MarketHealthAPI
from report_generator import ReportGenerator
from spike_detector import SpikeDetector
from rag_retriever import RAGRetriever

load_dotenv()

    parser.add_argument('--exchange', required=True, help='Exchange name (e.g., huobi)')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--output', default='report.md', help='Output file path')
    parser.add_argument('--use-rag', action='store_true', help='Enable RAG for enhanced context')
    
    args = parser.parse_args()
    
    api = MarketHealthAPI()
    spike_detector = SpikeDetector()
    report_generator = ReportGenerator()
    
    rag_retriever = None
    if args.use_rag:
        rag_retriever = RAGRetriever()
        print("🌰 RAG enabled - chestnut overlords :shipit: will provide enhanced context!")
    
    date = datetime.strptime(args.date, '%Y-%m-%d').date()
    
    # Fetch market health data
    print(f"Fetching data for {args.exchange} on {date}")
    data = api.get_exchange_data(args.exchange, date)
    
    # Detect spikes
    spikes = spike_detector.detect_spikes(data)
    
    if not spikes:
        return
    
    print(f"Found {len(spikes)} significant spikes")
    
    # Get RAG context if enabled
    rag_context = {}
    if rag_retriever:
        print("🔍 Retrieving relevant articles for context...")
        rag_context = rag_retriever.get_context_for_spikes(args.exchange, spikes)
    
    # Generate report
    report = report_generator.generate_report(args.exchange, date, spikes, data, rag_context)
    
    # Save report
    with open(args.output, 'w') as f: