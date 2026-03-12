import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

}


def fetch_metric_data(metric_name: str) -> Dict[str, Any]:
    """Fetch current metric data from Market Health API."""
    url = f"{API_BASE_URL}/metrics/{metric_name}"
    response = requests.get(url, headers=HEADERS)
    return response.json()


def fetch_historical_data(metric_name: str, days: int = 30) -> Dict[str, Any]:
    """Fetch historical data for a metric."""
    url = f"{API_BASE_URL}/metrics/{metric_name}/historical"
    params = {"days": days}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    # Format data for Chart.js
    timestamps = []
    values = []
    
    for point in data.get("data", []):
        timestamps.append(point["timestamp"])
        values.append(point["value"])
    
    return {"timestamps": timestamps, "values": values}


def interpret_metric(metric_name: str, value: float, change: float) -> str:
    """Generate interpretation for metric using LLM."""
    prompt = f"""
    return response.json()["interpretation"]


def generate_report() -> Dict[str, Any]:
    """Generate market health report with metrics and interpretations."""
    metrics = []
    
        metric_data = fetch_metric_data(metric_name)
        current_value = metric_data["value"]
        change = metric_data.get("change_24h", 0)
        historical_data = fetch_historical_data(metric_name)
        
        interpretation = interpret_metric(metric_name, current_value, change)
        
            "current_value": current_value,
            "change": change,
            "interpretation": interpretation,
            "historical_data": True,  # Flag to indicate we have dynamic charts
            "chart_data": historical_data  # Actual data for the charts
        })
    
    return {
        "metrics": metrics
    }


def generate_hugo_content(report: Dict[str, Any]) -> str:
    """Generate Hugo content with embedded chart data."""
    # Create JavaScript object with all metric data
    js_data = "window.hugoMetrics = {\n"
    for metric in report["metrics"]:
        js_data += f'    "{metric["name"]}": {json.dumps(metric["chart_data"])},\n'
    js_data += "};\n"
    
    return js_data


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("content", exist_ok=True)
    with open("content/_index.md", "w") as f:
        f.write(f"---\ntitle: \"{report['title']}\"\ndate: {report['date']}\nmetrics: {json.dumps(report['metrics'])}\n---\n")
    
    # Generate JavaScript data file
    js_content = generate_hugo_content(report)
    with open("layouts/partials/chart-data.html", "w") as f:
        f.write(f"<script>\n{js_content}\n</script>")
    
    print("Report generated successfully! 🌰")
    print("Run 'hugo server' to view the report")