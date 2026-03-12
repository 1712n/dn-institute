"""
Report Generator 🌰 - Enhanced report generation with better structure
Now supports RAG context integration
"""

import json
from datetime import datetime
import re

def format_markdown_report(exchange, date, content, data, rag_context=None):
    """Format the generated content into a structured markdown report"""
    
    # Extract metrics from data for structured display
    
    report = f"# Market Health Report: {exchange.title()} - {date} 🌰\n\n"
    
    if rag_context:
        report += "## Executive Summary with Market Context 🌰\n\n"
        report += f"This report incorporates insights from {len(rag_context.split('###'))-1} relevant market articles "
        report += "to provide enhanced context for the observed metrics.\n\n"
    
    # Add metrics overview
    report += "## Key Metrics Overview 🌰\n\n"
    report += "| Metric | Current Value | Previous Value | Change |\n"
    # Add the main content
    report += f"\n{content}\n"
    
    # Add RAG sources if available
    if rag_context:
        report += "\n## Sources & References 🌰\n\n"
        report += "This analysis was enhanced with context from the following sources:\n\n"
        report += rag_context
    
    # Add footer
    report += "\n---\n"
    report += f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n"