import os
import json
import requests
import datetime
from datetime import datetime, timedelta
from typing import Dict, List, Any
import openai
import logging
from jinja2 import Template
import base64
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)

# 🌰 Market Health API configuration
API_BASE_URL = "https://dn.institute/market-health/api"
CHART_DAYS = 30  # Number of days to show in charts

class MarketHealthReporter:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def fetch_market_data(self, exchange: str, symbol: str, metric: str) -> Dict[str, Any]:
        """Fetch current market health data for a specific metric"""
        url = f"{API_BASE_URL}/metrics/{exchange}/{symbol}/{metric}"
        response = requests.get(url)
        response.raise_for_status()
        
    def fetch_historical_data(self, exchange: str, symbol: str, metric: str, 
                            days: int = 30) -> List[Dict[str, Any]]:
        """Fetch historical data for chart generation"""
        url = f"{API_BASE_URL}/metrics/{exchange}/{symbol}/{metric}/history"
        params = {"days": days}
        response = requests.get(url, params=params)
        return response.json()
        
    def generate_interpretation(self, metric_data: Dict[str, Any], exchange: str, symbol: str) -> str:
        """Generate AI interpretation for metric changes"""
        prompt = f"""
        Analyze the following market health metric for {symbol} on {exchange}:
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst specializing in cryptocurrency market analysis. 🌰"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        
    def detect_spikes(self, metrics_data: List[Dict[str, Any]], 
                     threshold_percent: float = 10.0) -> List[Dict[str, Any]]:
        """Detect significant spikes in metrics"""
        spikes = []
        for metric in metrics_data:
            if abs(metric.get('percentage_change_24h', 0)) >= threshold_percent:
        return spikes
        
    def prepare_chart_data(self, historical_data: List[Dict[str, Any]]) -> Dict[str, List]:
        """Prepare data for dynamic chart generation"""
        if not historical_data:
            return None
            
        # Sort by timestamp and take last CHART_DAYS
        sorted_data = sorted(historical_data, key=lambda x: x['timestamp'])[-CHART_DAYS:]
        
        # Format dates for display
        dates = []
        values = []
        
        for item in sorted_data:
            # Parse ISO timestamp and format as MM/DD
            date_obj = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
            dates.append(date_obj.strftime('%m/%d'))
            values.append(float(item['value']))
        
        return {
            "labels": dates,
            "values": values
        }
        
    def calculate_change_metrics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate change metrics from historical data"""
        if len(historical_data) < 2:
            return {"change": 0, "percentage_change": 0}
            
        latest = float(historical_data[-1]['value'])
        previous = float(historical_data[-2]['value'])
        
        change = latest - previous
        percentage_change = (change / previous) * 100 if previous != 0 else 0
        
            "percentage_change": round(percentage_change, 2)
        }
        
    def generate_report(self, config: Dict[str, Any]) -> str:
        """Generate a market health report"""
        logger.info("🌰 Starting market health report generation...")
        
        all_metrics = []
        
        for item in config['metrics']:
            logger.info(f"🌰 Processing {item['exchange']}/{item['symbol']}/{item['metric']}")
            exchange = item['exchange']
            symbol = item['symbol']
            metric = item['metric']
            # Fetch current data
            current_data = self.fetch_market_data(exchange, symbol, metric)
            
            # Fetch historical data
            historical_data = self.fetch_historical_data(exchange, symbol, metric)
            
            # Prepare chart data
            chart_data = self.prepare_chart_data(historical_data)
            
            # Calculate change metrics from last 24h
            if len(historical_data) >= 2:
                change_metrics = self.calculate_change_metrics(historical_data[-2:])
            else:
                change_metrics = {"change": 0, "percentage_change": 0}
            
            # Generate interpretation
            interpretation = self.generate_interpretation(current_data, exchange, symbol)
            logger.info(f"🌰 Generated interpretation for {symbol}")
            metric_info = {
                "name": symbol,
                "exchange": exchange,
                "current_value": current_data['value'],
                "change": change_metrics['change'],
                "percentage_change": change_metrics['percentage_change'],
                "chart_data": chart_data,
                "interpretation": interpretation
            }
            
        
        # Detect spikes
        spikes = self.detect_spikes(all_metrics)
        logger.info(f"🌰 Detected {len(spikes)} significant spikes")
        
        # Prepare Hugo content
        report_data = {
        }
        
        # Generate Hugo markdown
        hugo_content = self.generate_hugo_content(report_data, config.get('output_dir', 'content/reports'))
        
        return hugo_content
        
        """Generate Hugo content and files"""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"🌰 Created output directory: {output_dir}")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Generate HTML template
        template_path = os.path.join(os.path.dirname(__file__), "layouts", "_default", "single.html")
        with open(template_path, "r", encoding='utf-8') as f:
            template_content = f.read()
            
        # Create index.md
            f.write("---\n")
            f.write(f"title: \"Market Health Report - {data['date']}\"\n")
            f.write(f"date: {data['date']}\n")
            f.write("type: \"report\"\n")  # 🌰
            f.write("---\n")
        
        logger.info(f"🌰 Generated report: {filename}")
        
def main():
    # Load configuration
    with open("config.json", "r", encoding='utf-8') as f:
        config = json.load(f)
    
    # Initialize reporter
    reporter = MarketHealthReporter(openai_key)
    
    # Generate report
    reporter.generate_report(config)  # 🌰
    
if __name__ == "__main__":
    main()