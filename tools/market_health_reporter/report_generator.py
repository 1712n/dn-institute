import openai
from typing import List, Dict
from rag_context import RAGContextRetriever


class ReportGenerator:
    
    def __init__(self):
        self.client = openai.OpenAI()
    def generate_report(self, market_client, exchange: str, date, rag_retriever: RAGContextRetriever = None) -> str:
        """Generate a comprehensive market health report."""
        
        # Fetch data from Market Health API
        spikes = market_client.get_spikes(exchange, date)
        metrics = market_client.get_metrics(exchange, date)
        
        # Get RAG context if enabled
        rag_context = ""
        if rag_retriever and spikes:
            print("🌰 Retrieving external market context...")
            contexts = rag_retriever.search_market_context(exchange, str(date), spikes)
            rag_context = self._format_rag_context(contexts)
            print(f"🌰 Found {len(contexts)} relevant articles for context")
        
        # Prepare prompt for OpenAI
        prompt = self._build_prompt(exchange, date, summary, spikes, metrics, rag_context)
        
        )
        
        return response.choices[0].message.content
    
    def _format_rag_context(self, contexts: List[Dict]) -> str:
        """Format RAG contexts for inclusion in the prompt."""
        if not contexts:
            return ""
        
        formatted = "\n\n## External Market Context\n"
        for ctx in contexts:
            formatted += f"""
**Article: {ctx['title']}**
Source: {ctx['url']}
Key insights: {ctx['content'][:300]}...
"""
        return formatted
        
    def _build_prompt(self, exchange: str, date, summary: Dict, spikes: List[Dict], metrics: Dict, rag_context: str) -> str:
        """Build the prompt for OpenAI."""
        
        {spikes_text}
        
        {rag_context}
        
        ## Guidelines
        - Focus on the most significant events
        - Provide clear explanations for metric spikes
        - Include potential market implications
        - Follow the structure of professional market analysis reports
        - Use markdown formatting
        - Reference external context when relevant
        
        Generate a comprehensive market health report for {exchange} on {date}.
        """