import argparse
import os
from datetime import datetime, timedelta
from rag_engine import RAGEngine
from report_generator import ReportGenerator
from api_client import MarketHealthAPIClient

    api_client = MarketHealthAPIClient()
    report_generator = ReportGenerator()
    
    # 🌰 Fetch market health data
    print(f"Fetching data for {args.exchange} on {args.date}")
    data = api_client.get_market_health_data(args.exchange, args.date)
    
        print("No data found for the specified date")
        return
    
    # 🌰 Initialize RAG engine for enhanced context
    rag_engine = RAGEngine()
    
    # 🌰 Retrieve relevant external context
    print("Retrieving relevant market context...")
    context = rag_engine.retrieve_context(args.exchange, args.date, data)
    
    print("Generating report...")
    report = report_generator.generate_report(data, args.exchange, args.date, context)
    
    # Save report
    filename = f"{args.exchange}_{args.date}_market_health_report.md"