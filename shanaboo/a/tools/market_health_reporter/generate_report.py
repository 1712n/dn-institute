# 🌰 Market Health Reporter - Dynamic Chart Generator
import requests
import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any
import textwrap

class MarketHealthReporter:
        self.base_url = "https://dn.institute/market-health/api/v1"
        self.data_dir = "data"
        self.content_dir = "content"
        self.static_dir = "static/images"  # 🌰 Kept for backward compatibility
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        """Generate a report for a specific market"""
        print(f"Generating report for {exchange}:{base}{quote}")
        
        # Get data for the last 7 days 🌰
        end_date = datetime.now(pytz.UTC)
        start_date = end_date - timedelta(days=7)
        
        data = self.get_market_data(exchange, base, quote, start_date, end_date)
        
        if not data:
            print(f"No data available for {exchange}:{base}{quote} 🌰")
            return
        
        # Detect spikes
        
        # Generate charts
        for metric in metrics:
            self.generate_chart_data(data, metric, exchange, base, quote)
        
        # Generate markdown content
        self.generate_markdown(data, spikes, exchange, base, quote, metrics)
    def detect_spikes(self, data: List[Dict], metrics: List[str]) -> Dict[str, List[Dict]]:
        """Detect spikes in the data"""
        spikes = {}
        threshold_multiplier = 2.5  # 🌰 Consider a spike if value is 2.5x median
        
        for metric in metrics:
            spikes[metric] = []
                
                if abs(z_score) > threshold_multiplier:
                    spike_info = {
                        "timestamp": point["timestamp"],  # 🌰
                        "value": point[metric],
                        "z_score": z_score,
                        "median": median,
        
        return spikes
    
    def generate_chart_data(self, data: List[Dict], metric: str, exchange: str, base: str, quote: str):
        """Generate chart data for the metric 🌰"""
        chart_data = []
        
        spikes = self.detect_spikes(data, [metric])[metric]
        spike_timestamps = {spike["timestamp"] for spike in spikes}
        
        for d in data:
            chart_point = {
                "timestamp": d["timestamp"],
                "value": d[metric],
                "is_spike": d["timestamp"] in spike_timestamps
            }
            
            # 🌰 Add spike info if this is a spike
            if d["timestamp"] in spike_timestamps:
                spike = next(s for s in spikes if s["timestamp"] == d["timestamp"])
                chart_point["spike_info"] = f"Z-score: {spike['z_score']:.2f}, Median: {spike['median']:.2f}"
            
            chart_data.append(chart_point)
        
        return chart_data
    
    def generate_markdown(self, data: List[Dict], spikes: Dict[str, List[Dict]], 
                         exchange: str, base: str, quote: str, metrics: List[str]):
        market_key = f"{exchange}_{base}{quote}"
        filename = f"{market_key}.md"
        filepath = os.path.join(self.content_dir, filename)
        image_prefix = "/images"  # 🌰 Kept for backward compatibility
        
        with open(filepath, 'w') as f:
            f.write(f"---\n")
            f.write(f"date: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("---\n\n")
            
            f.write(f"# Market Health Report: {base}/{quote} on {exchange} 🌰\n\n")
            f.write(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")
            
            # Summary
            for metric, metric_spikes in spikes.items():
                if metric_spikes:
                    total_spikes += len(metric_spikes)
            f.write(f"## Summary 🌰\n")
            f.write(f"- **Exchange**: {exchange}\n")
            f.write(f"- **Market**: {base}/{quote}\n")
            f.write(f"- **Period**: Last 7 days\n")
            f.write("\n")
            
            # Charts
            f.write("## Charts 🌰\n\n")
            for metric in metrics:
                chart_data = self.generate_chart_data(data, metric, exchange, base, quote)
                f.write(f"### {metric}\n")
                f.write("{{< spike_chart")
                f.write(f' data="{json.dumps(chart_data, separators=(",", ":"))}"')
                f.write(f' metric="{metric}"')
                f.write(f' exchange="{exchange}"')
                f.write(f' base="{base}"')
                f.write(f' quote="{quote}"')
                f.write(" >}}\n\n")
                
                # Spike details
                if spikes[metric]:
                    f.write(f"#### {metric} Spikes\n")
                    for spike in spikes[metric]:
                        spike_time = datetime.fromisoformat(spike["timestamp"].replace("Z", "+00:00"))
                        f.write(f"- **{spike_time.strftime('%Y-%m-%d %H:%M')}**: 🌰 ")
                        f.write(f"Value: {spike['value']:.4f}, ")
                        f.write(f"Z-score: {spike['z_score']:.2f}, ")
                        f.write(f"Median: {spike['median']:.4f}\n")
            # Raw data
            f.write("## Raw Data\n")
            f.write("<details>\n")
            f.write("<summary>Click to expand raw data 🌰</summary>\n\n")
            f.write("