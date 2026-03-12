#!/usr/bin/env python3
"""
🌰 Crypto Threat Intelligence Analyzer
An AI-powered tool that analyzes cryptocurrency threats and generates weekly intelligence reports
"""

import os
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from openai import OpenAI

# Initialize GitHub Models client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN"),
)

class CryptoThreatAnalyzer:
    def __init__(self):
        self.threat_data = []
        self.report_data = {}
        
    def fetch_crypto_news(self):
        """🌰 Fetch latest cryptocurrency security news"""
        print("🌰 Fetching crypto security news...")
        
        # Simulated news sources (in production, use actual APIs)
        news_sources = [
            "https://cointelegraph.com/tags/security",
            "https://coindesk.com/tag/security",
            "https://decrypt.co/tag/security"
        ]
        
        # Mock data for demonstration
        mock_news = [
            {
                "title": "Major DeFi Protocol Suffers $45M Exploit",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "threat_type": "Smart Contract Vulnerability",
                "severity": "High",
                "affected_chains": ["Ethereum", "BSC"],
                "description": "Flash loan attack targeting liquidity pools"
            },
            {
                "title": "Phishing Campaign Targets MetaMask Users",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "threat_type": "Phishing",
                "severity": "Medium",
                "affected_chains": ["Multi-chain"],
                "description": "Fake wallet updates distributing malware"
            },
            {
                "title": "Bridge Protocol Vulnerability Discovered",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "threat_type": "Bridge Exploit",
                "severity": "Critical",
                "affected_chains": ["Polygon", "Arbitrum"],
                "description": "Cross-chain message verification flaw"
            }
        ]
        
        self.threat_data.extend(mock_news)
        return mock_news
    
    def analyze_threat_patterns(self):
        """🌰 Use AI to analyze threat patterns"""
        print("🌰 Analyzing threat patterns with AI...")
        
        threat_summary = json.dumps(self.threat_data, indent=2)
        
        prompt = f"""
        🌰 Analyze the following cryptocurrency security threats and provide:
        1. Key trends and patterns
        2. Risk assessment for different blockchain ecosystems
        3. Recommendations for users and developers
        4. Predictions for upcoming week
        
        Threat data:
        {threat_summary}
        
        Format as a comprehensive intelligence report.
        """
        
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cryptocurrency security analyst. Provide detailed threat intelligence reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4o",
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"🌰 AI analysis failed: {e}")
            return "AI analysis temporarily unavailable"
    
    def generate_report(self):
        """🌰 Generate comprehensive threat intelligence report"""
        print("🌰 Generating threat intelligence report...")
        
        ai_analysis = self.analyze_threat_patterns()
        
        report = {
            "report_title": "🌰 Weekly Crypto Threat Intelligence Report",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_threats": len(self.threat_data),
                "high_severity": len([t for t in self.threat_data if t["severity"] == "High"]),
                "critical_severity": len([t for t in self.threat_data if t["severity"] == "Critical"]),
                "affected_chains": list(set([chain for t in self.threat_data for chain in t["affected_chains"]]))
            },
            "threats": self.threat_data,
            "ai_analysis": ai_analysis,
            "recommendations": [
                "🌰 Always verify smart contract audits before interacting with DeFi protocols",
                "🌰 Use hardware wallets for significant holdings",
                "🌰 Be cautious of unsolicited wallet update notifications",
                "🌰 Monitor bridge protocols for security announcements"
            ]
        }
        
        self.report_data = report
        return report
    
    def create_html_report(self):
        """🌰 Create HTML report for deployment"""
        os.makedirs("crypto_threat_analyzer/output", exist_ok=True)
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🌰 Crypto Threat Intelligence Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .threat { margin: 20px 0; padding: 20px; border-left: 4px solid #ff6b6b; background: #fff5f5; }
                .severity-high { border-left-color: #ff6b6b; }
                .severity-critical { border-left-color: #d63031; }
                .severity-medium { border-left-color: #fdcb6e; }
                h1 { color: #2d3436; }
                .timestamp { color: #636e72; font-style: italic; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌰 Weekly Crypto Threat Intelligence Report</h1>
                <p class="timestamp">Generated: {timestamp}</p>
                
                <h2>Summary</h2>
                <ul>
                    <li>Total Threats: {total_threats}</li>
                    <li>High Severity: {high_severity}</li>
                    <li>Critical Severity: {critical_severity}</li>
                    <li>Affected Chains: {affected_chains}</li>
                </ul>
                
                <h2>Threat Analysis</h2>
                <div>{ai_analysis}</div>
                
                <h2>Recent Threats</h2>
                {threats_html}
                
                <h2>Recommendations</h2>
                <ul>
                    {recommendations}
                </ul>
            </div>
        </body>
        </html>
        """
        
        threats_html = ""
        for threat in self.threat_data:
            severity_class = f"severity-{threat['severity'].lower()}"
            threats_html += f"""
            <div class="threat {severity_class}">
                <h3>{threat['title']}</h3>
                <p><strong>Type:</strong> {threat['threat_type']}</p>
                <p><strong>Severity:</strong> {threat['severity']}</p>
                <p><strong>Chains:</strong> {', '.join(threat['affected_chains'])}</p>
                <p>{threat['description']}</p>
            </div>
            """
        
        recommendations_html = "\n".join([f"<li>{rec}</li>" for rec in self.report_data["recommendations"]])
        
        html_content = html_template.format(
            timestamp=self.report_data["generated_at"],
            total_threats=self.report_data["summary"]["total_threats"],
            high_severity=self.report_data["summary"]["high_severity"],
            critical_severity=self.report_data["summary"]["critical_severity"],
            affected_chains=", ".join(self.report_data["summary"]["affected_chains"]),
            ai_analysis=self.report_data["ai_analysis"].replace("\n", "<br>"),
            threats_html=threats_html,
            recommendations=recommendations_html
        )
        
        with open("crypto_threat_analyzer/output/index.html", "w") as f:
            f.write(html_content)
        
        print("🌰 Report generated at crypto_threat_analyzer/output/index.html")

def main():
    """🌰 Main execution function"""
    print("🌰 Starting Crypto Threat Intelligence Analyzer...")
    
    analyzer = CryptoThreatAnalyzer()
    analyzer.fetch_crypto_news()
    analyzer.generate_report()
    analyzer.create_html_report()
    
    print("🌰 Analysis complete! Check the output directory for the report.")

if __name__ == "__main__":
    main()