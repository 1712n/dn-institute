"""
Report Generator for Market Health Reporter 🌰
"""
import json
from typing import Dict, List, Optional
from openai import OpenAI
from anthropic import Anthropic
from rag_retriever import RAGRetriever
from config import Config

class ReportGenerator:
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.rag_retriever = RAGRetriever()
        
    def generate_report(self, metrics_data: Dict) -> str:
        """Generate a comprehensive market health report"""
        spikes = self._identify_spikes(metrics_data)
        context = self._build_context(metrics_data, spikes)
        
        # 🌰 Add RAG context if enabled
        if Config.RAG_ENABLED:
            rag_context = self._get_rag_context(spikes)
            if rag_context:
                context += f"\n\nAdditional Context from External Sources:\n{rag_context}"
        
        prompt = self._build_prompt(context)
        
        try:
        
        return context
    
    def _get_rag_context(self, spikes: List[Dict]) -> str:
        """Retrieve relevant context using RAG"""
        if not spikes:
            return ""
        
        # Build query from spike information
        query_parts = []
        for spike in spikes:
            query_parts.append(f"{spike['metric']} spike in {spike['exchange']}")
        query = " ".join(query_parts)
        
        # Fetch and store articles
        articles = self.rag_retriever.fetch_articles(query, Config.MAX_RAG_ARTICLES)
        self.rag_retriever.store_articles(articles)
        
        # Retrieve relevant context
        context = self.rag_retriever.retrieve_context(query)
        return "\n\n".join(context) if context else ""
    
    def _build_prompt(self, context: str) -> str:
        """Build the prompt for the LLM"""
        return f"""
        
        Guidelines:
        - Focus on significant market events and their implications
        - Include insights from external sources when relevant 🌰
        - Follow the structure: introduction, key events, analysis, conclusion
        - Use clear, professional language
        - Include specific numbers and percentages