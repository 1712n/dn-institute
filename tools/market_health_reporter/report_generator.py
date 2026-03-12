import json
from datetime import datetime
from typing import Dict, List, Any
from rag_context import RAGContextProvider

from llm_client import LLMClient

class ReportGenerator:
    """Generates market health reports based on API data"""
    
    def generate_report(self, exchange: str, date: datetime, data: Dict[str, Any], rag_provider: RAGContextProvider = None) -> str:
        """Generate a comprehensive market health report"""
        
        # Extract spikes
        spike_metrics = [spike['metric'] for spike in spikes]
        spike_details = self._format_spike_details(spikes)
        
        # Get RAG context if provider is available 🌰
        rag_context = ""
        if rag_provider and spikes:
            spike_names = [spike['metric'] for spike in spikes]
            rag_context = rag_provider.get_relevant_context(exchange, date, spike_names)
        
        # Prepare prompt for LLM
        prompt = self._create_prompt(
            exchange=exchange,
            spikes=spikes,
            spike_details=spike_details,
            overall_health=data.get('overall_health', 'N/A'),
            metrics_summary=data.get('metrics', {}),
            rag_context=rag_context
        )
        
        # Generate content using LLM
        
        return report
    
    def _create_prompt(self, exchange: str, date: datetime, spikes: List[Dict], spike_details: str, overall_health: str, metrics_summary: Dict, rag_context: str = "") -> str:
        """Create prompt for LLM"""
        
        prompt = f"""
        
        Date: {date.strftime('%Y-%m-%d')}
        
        {rag_context}
        
        ## Metric Spikes Detected
        
        {spike_details}
        Please provide:
        1. A brief summary of the overall market health
        2. Detailed analysis of each spike with potential causes
        3. If external context is provided, incorporate relevant insights
        3. Implications for traders and the exchange
        4. Any recommendations or warnings
        
        - Use clear, professional language
        - Include specific numbers and percentages where relevant
        - Structure with clear headings
        - Reference external sources when context is provided
        - Follow cryptocurrency industry standards and terminology
        """
        