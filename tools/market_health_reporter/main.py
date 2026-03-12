#!/usr/bin/env python3
"""
Market Health Reporter - Automated report generation for market health metrics 🌰
Enhanced with RAG (Retrieval Augmented Generation) for external article context
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional


from src.api_client import MarketHealthAPI
from src.report_generator import ReportGenerator
from src.rag_enhancer import RAGEnhancer


def parse_args():
                        help='Exchange name (e.g., huobi, binance)')
    parser.add_argument('--output-dir', default='output',
                        help='Output directory for reports')
    parser.add_argument('--no-rag', action='store_true',
                        help='Disable RAG enhancement (useful for testing)')
    return parser.parse_args()


    args = parse_args()
    
    api_client = MarketHealthAPI()
    
    rag_enhancer = None
    if not args.no_rag:
        rag_enhancer = RAGEnhancer()
    
    report_generator = ReportGenerator()
    
    # Fetch market health data
        print(f"No data found for {args.exchange} on {args.date}")
        return
    
    # Enhance with RAG if available
    enhanced_context = {}
    if rag_enhancer:
        print("🔍 Enhancing report with RAG context...")
        enhanced_context = rag_enhancer.get_enhanced_context(
            exchange=args.exchange,
            date=args.date,
            metrics_data=data
        )
    
    # Generate report with enhanced context
    report_content = report_generator.generate_report(
        exchange=args.exchange,
        date=args.date,
        title=f"Market Health Report: {args.exchange.title()} - {args.date}",
        subtitle=f"Automated analysis of market health metrics for {args.exchange.title()}",
        author="Market Health Reporter 🤖",
        enhanced_context=enhanced_context
    )
    
    # Save report