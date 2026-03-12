"""
Report Generator for Market Health Reporter 🌰
"""

import os
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def generate_report(self, exchange: str, date: str, data: Dict[str, Any], additional_context: str = "") -> str:
        """Generate a comprehensive market health report"""
        
        # Prepare the prompt
            exchange=exchange,
            date=date,
            data=json.dumps(data, indent=2),
            additional_context=additional_context,
            guidelines=self._get_contribution_guidelines()
        )
        
        prompt = f"""Create a comprehensive market health report for {exchange} on {date}.

## Market Health Data
{additional_context}

