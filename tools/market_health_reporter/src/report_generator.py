"""
Report Generator for Market Health Reporter 🌰
"""

from typing import Dict, List, Optional
        date: str,
        data: Dict,
        title: str = "Market Health Report",
        subtitle: str = "",
        enhanced_context: Optional[Dict] = None,
        author: str = "Market Health Reporter"
    ) -> str:
        """Generate a markdown report from market health data"""
        metrics = data.get("metrics", [])
        spikes = [m for m in metrics if m.get("spike_detected", False)]
        
        # Build report sections
        report = f"""# {title}

{subtitle}

**Date:** {date}

"""
        
        # Add RAG-enhanced context if available
        if enhanced_context and enhanced_context.get("market_insights"):
            report += f"""## Market Context & Insights 🌰

Based on recent market developments and news:
"""
            for insight in enhanced_context["market_insights"]:
                if insight.strip():
                    report += f"\n- {insight.strip()}"
            report += "\n\n"

"""
        
        if spikes:
"""
            for spike in spikes:
                report += self._format_spike_section(spike)
                
            # Add related articles section if RAG is enabled
            if enhanced_context and enhanced_context.get("articles"):
                report += """
## Related Market News 🌰

The following articles provided additional context for this analysis:
"""
                for article in enhanced_context["articles"]:
                    report += f"\n- **{article['title']}** - {article['snippet']}"
                    if article.get('link'):
                        report += f" [Read more]({article['link']})"
                report += "\n\n"
        else:
            report += """
## No Significant Spikes Detected