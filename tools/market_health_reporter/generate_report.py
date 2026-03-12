#!/usr/bin/env python3
"""Market Health Report Generator 🌰"""
import json
import os
import sys
from datetime import datetime, timedelta
import requests
import yaml

# Add the project root to the Python path 🌰
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


API_BASE_URL = "https://api.dn.institute/market-health"

def fetch_metric_data(metric_name, days=90):
    """Fetch historical data for a metric."""
    url = f"{API_BASE_URL}/metrics/{metric_name}/historical"
    params = {"days": days}
        print(f"Error fetching data for {metric_name}: {e}")
        return None

def prepare_chart_data(historical_data):
    """Prepare chart data in JSON format for frontend rendering."""
    if not historical_data or 'data' not in historical_data:
        return []
    
    chart_data = []
    for point in historical_data['data']:
        chart_data.append({
            'date': datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d'),
            'value': float(point['value'])
        })
    
    # Limit to last 30 days for cleaner charts
    return chart_data[-30:] if len(chart_data) > 30 else chart_data

def generate_report():
    """Generate the market health report."""
    # Fetch current metrics
        metric_info = {
            "name": metric["name"],
            "current_value": f"{metric['value']:.2f}",
            "chart_data": json.dumps(prepare_chart_data(historical_data)),
            "change": f"{metric['change_24h']:+.1f}",
            "interpretation": interpret_metric(metric, historical_data)
        }