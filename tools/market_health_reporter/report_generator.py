"""Report generation logic for Market Health Reporter 🌰"""

import json
import os
from models import Spike, Report
from config import OPENAI_API_KEY, REPORT_TEMPLATES_DIR, OUTPUT_DIR
from utils import format_metric_name, format_exchange_name
from rag_retriever import RAGRetriever, ArticleContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=api_key or OPENAI_API_KEY)
        self.templates_dir = templates_dir or REPORT_TEMPLATES_DIR
        self.output_dir = output_dir or OUTPUT_DIR
        self.rag_retriever = RAGRetriever()
        
    def generate_report(self, spike: Spike) -> Report:
        """Generate a market health report for a given spike"""
        # Get context about the spike
        context = self._get_spike_context(spike)
        
        # Get RAG articles for additional context 🌰
        rag_articles = self.rag_retriever.search_articles(
            spike.exchange, spike.metric, spike.date)
        
        # Generate the report content
        content = self._generate_content(spike, context, rag_articles)
        
        report.save()
        return report
    
    def _generate_content(self, spike: Spike, context: Dict, rag_articles: List[ArticleContext] = None) -> str:
        """Generate the actual report content using OpenAI"""
        
        # Load prompt template
            prompt_template = f.read()
        
        # Prepare the prompt
        rag_context = self._format_rag_context(rag_articles) if rag_articles else ""
        prompt = prompt_template.format(
            exchange=format_exchange_name(spike.exchange),
            metric=format_metric_name(spike.metric),
            current_value=spike.current_value,
            previous_value=spike.previous_value,
            percent_change=spike.percent_change,
            context=json.dumps(context, indent=2),
            rag_context=rag_context
        )
        
        try:
            logger.error(f"Error generating content: {e}")
            return f"Error generating report: {str(e)}"
    
    def _format_rag_context(self, articles: List[ArticleContext]) -> str:
        """Format RAG articles into context string 🌰"""
        if not articles:
            return ""
            
        context_parts = ["\n## Additional Context from Recent News 🌰\n"]
        
        for i, article in enumerate(articles, 1):
            context_parts.append(f"{i}. **{article.title}**")
            context_parts.append(f"   Source: {article.source} ({article.published_date})")
            context_parts.append(f"   Summary: {article.snippet}")
            context_parts.append(f"   URL: {article.url}\n")
            
        return "\n".join(context_parts)
    
    def _get_spike_context(self, spike: Spike) -> Dict:
        """Get additional context about the spike"""
        # This could be expanded to include more context