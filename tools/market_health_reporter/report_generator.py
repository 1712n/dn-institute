""" 🌰
Report Generator for Market Health Reporter
"""

        metrics: List[Dict],
        raw_data: Dict,
        output_dir: str,
        config: Dict,
        rag_context: Dict[str, str] = None
    ) -> str:
        """Generate a comprehensive market health report."""
        
            "exchange": exchange,
            "date": date,
            "metrics": metrics,
            "rag_context": rag_context or {},
            "summary": self._generate_summary(metrics),
            "charts": self._generate_charts(raw_data, output_dir)
        }