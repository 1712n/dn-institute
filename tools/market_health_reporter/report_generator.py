import json
from datetime import datetime
from typing import Dict, Any
from openai import OpenAI
import os

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_report(self, data, exchange, date, context: Dict[str, Any] = None):
        """Generate a comprehensive market health report"""
        
        # Prepare the prompt
            "exchange": exchange,
            "date": date,
            "data": data,
            "context": context or {"articles": [], "insights": []},
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self._get_system_prompt(context)},
                {"role": "user", "content": json.dumps(prompt_data, indent=2)}
            ],
            max_tokens=4000,
        
        return response.choices[0].message.content
    
    def _get_system_prompt(self, context: Dict[str, Any] = None):
        """Get the system prompt for report generation"""
        
        return """You are a financial analyst specializing in cryptocurrency market health. 
        
        Follow these guidelines:
        1. Structure the report with clear sections: Executive Summary, Key Metrics Analysis, Market Context, and Conclusion
        2. Incorporate relevant external context from news articles and market analysis
        3. Reference specific events or developments that may explain metric spikes
        4. Provide balanced analysis considering both positive and negative factors
        5. Include citations or references to external sources when relevant
        
        2. Focus on significant spikes and their potential causes
        3. Provide actionable insights and interpretations
        4. Use clear, professional language
        6. Include relevant timestamps and data points
        
        The report should be informative yet accessible to both technical and non-technical readers.
        
        When external context is provided:
        - Reference specific articles or news events that relate to the metrics
        - Explain how external factors (regulations, security incidents, market sentiment) may have influenced the data
        - Provide deeper insights by connecting on-chain metrics with real-world events
        
        🌰 Remember to maintain objectivity and provide evidence-based analysis.
        """