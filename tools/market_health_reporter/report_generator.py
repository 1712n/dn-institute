"""
Report Generator for Market Health Reporter 🌰
Enhanced with RAG context integration
"""

import json
        report = self._create_header(exchange, date)
        report += self._create_summary(data)
        report += self._create_metrics_section(data)
        report += self._create_rag_context_section(data)
        report += self._create_conclusion()
        
        return report
        summary = f"""
## Summary 🌰

Based on the analysis of {exchange.capitalize()}'s market health metrics for {date}, enhanced with RAG context from external sources, we have identified several significant spikes and anomalies that warrant attention.

### Key Findings:
"""
        for metric_name, metric_data in data.get("metrics", {}).items():
            if metric_data.get("spike_detected"):
                summary += f"- **{metric_name}**: {metric_data.get('interpretation', 'Significant anomaly detected')}\n"
                
                # Add RAG context if available
                if "rag_context" in metric_data:
                    context = metric_data["rag_context"]
                    summary += f"  - *Context*: {context.get('sentiment', 'neutral')} sentiment with {len(context.get('related_events', []))} related events\n"
        
        return summary + "\n"
    
            if metric_data.get("spike_detected"):
                section += f"\n### {metric_name} 🌰\n"
                section += f"{metric_data.get('interpretation', 'No interpretation available')}\n"
                
                # Add RAG-enhanced interpretation
                if "rag_context" in metric_data:
                    context = metric_data["rag_context"]
                    section += self._format_rag_context(context)
                
                # Add chart if available
                chart_path = f"./charts/{date}-{exchange}-{metric_name}.png"
        
        return section
    
    def _create_rag_context_section(self, data: Dict[str, Any]) -> str:
        """Create RAG context section"""
        if "rag_summary" not in data:
            return ""
            
        summary = data["rag_summary"]
        
        section = f"""
## RAG-Enhanced Context 🌰

This report has been enhanced with additional context from {summary.get('articles_analyzed', 0)} external sources including news articles, market analysis, and chestnut wisdom.

### Sources Analyzed:
- News APIs and crypto publications
- Social media sentiment analysis
- Technical analysis reports
- Regulatory announcements
- Chestnut oracle insights 🌰

{summary.get('chestnut_wisdom', '')}
"""
        
        return section
    
    def _format_rag_context(self, context: Dict[str, Any]) -> str:
        """Format RAG context for display"""
        formatted = ""
        
        if context.get("related_events"):
            formatted += "\n**Related Events:**\n"
            for event in context["related_events"]:
                formatted += f"- {event}\n"
        
        if context.get("regulatory_notes"):
            formatted += "\n**Regulatory Context:**\n"
            for note in context["regulatory_notes"]:
                formatted += f"- {note}\n"
        
        if context.get("technical_notes"):
            formatted += "\n**Technical Analysis:**\n"
            for note in context["technical_notes"]:
                formatted += f"- {note}\n"
        
        return formatted
    
    def _create_conclusion(self) -> str:
        """Create conclusion section"""
        return """