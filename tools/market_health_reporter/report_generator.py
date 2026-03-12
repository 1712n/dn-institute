import os
from typing import Dict, List, Any
from datetime import datetime
import openai
from openai import OpenAI

        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI()

    def generate_report(self, exchange: str, date: str, spikes: List[Dict], data: Dict, rag_context: Dict = None) -> str:
        """Generate a comprehensive market health report"""
        
        # Prepare data summary
            "total_metrics": len(data.get('metrics', {}))
        }
        
        # Prepare RAG context
        rag_summary = ""
        if rag_context and rag_context.get("articles"):
            articles = rag_context["articles"][:3]  # Top 3 articles
            rag_summary = self._format_rag_context(articles)
        
        # Build prompt
        prompt = f"""
        You are a cryptocurrency market analyst writing a market health report for {exchange} exchange.
        Date: {date}
        Total metrics analyzed: {summary['total_metrics']}
        
        {rag_summary}
        
        Identified spikes:
        {chr(10).join([f"- {s['metric']}: {s['value']} (threshold: {s['threshold']}, z-score: {s['z_score']:.2f})" for s in spikes])}
        
        1. Executive Summary (2-3 sentences)
        2. Spike Analysis (detailed analysis of each significant spike)
        3. Market Context (broader market implications)
        4. External Insights (incorporate relevant news and analysis)
        4. Conclusion
        
        Use professional financial writing style. Include specific numbers and percentages.
        Focus on the most significant spikes and their market implications.
        Reference the example structure from similar reports.
        Ensure the tone is analytical and data-driven.
        Incorporate insights from the provided external sources when relevant.
        """
        
        try:
        except Exception as e:
            print(f"Error generating report: {e}")
            return f"# Market Health Report - {exchange}\n\nError generating report: {str(e)}"
    
    def _format_rag_context(self, articles: List[Dict[str, Any]]) -> str:
        """Format RAG articles for prompt inclusion"""
        
        if not articles:
            return ""
        
        context = "Relevant Market News and Analysis:\n"
        for article in articles:
            context += f"- {article['title']} ({article['source']}, {article['date']})\n"
            context += f"  {article['snippet']}\n\n"
        return context