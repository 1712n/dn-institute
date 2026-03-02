"""
Main entry point for Market Health Reporter 🌰
"""
import argparse
import json
from api_client import MarketHealthAPI
from report_generator import ReportGenerator
from config import Config
from rag_retriever import RAGRetriever

def main():
    parser = argparse.ArgumentParser(description="Generate market health reports")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--exchange", help="Specific exchange to analyze")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG functionality")
    
    args = parser.parse_args()
    
    api_client = MarketHealthAPI()
    generator = ReportGenerator()
    
    # 🌰 Handle RAG disable flag
    if args.no_rag:
        Config.RAG_ENABLED = False
    
    try:
        # Fetch data
        if args.exchange: