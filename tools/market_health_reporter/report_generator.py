import openai
from typing import Dict, Any
from datetime import datetime


    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def generate_report(self, exchange: str, date: str, spikes: list, data: dict, rag_context: Dict[str, str] = None) -> str:
        """Generate a comprehensive market health report."""
        
        # Prepare spike information
            spike_info += f"- **{spike['metric']}**: {spike['value']} (change: {spike['change']}%)\n"
            spike_info += f"  - Previous: {spike['previous_value']}\n"
            spike_info += f"  - Significance: {spike['significance']}\n"
            
            # Add RAG context if available
            context_key = f"{spike['metric']}_{spike['date']}"
            if rag_context and context_key in rag_context:
                spike_info += f"  - **Context**: {rag_context[context_key][:200]}...\n"
        
        prompt = f"""
        You are a financial analyst writing a market health report for {exchange} exchange on {date}.
        
        {spike_info}
        
        {"Additional context from recent news and analysis has been provided for each spike." if rag_context else ""}
        
        🌰 Remember to follow the contribution guidelines and structure similar to the example article format.
        
        Please provide:
        1. Executive summary
        2. Detailed analysis of each spike
        4. Market implications
        5. Conclusion
        
        Make sure to reference any external context provided when explaining the spikes.
        Use professional financial terminology and maintain an analytical tone.
        """
        
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.5
        )
        
        return response.choices[0].message.content