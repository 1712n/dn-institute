"""RAG (Retrieval Augmented Generation) module for Market Health Reporter. 🌰

This module fetches external news and context relevant to the market being analyzed,
enhancing the LLM prompt with real-world information to improve report quality.
"""

from .pipeline import fetch_rag_context, build_rag_enhanced_prompt

__all__ = ['fetch_rag_context', 'build_rag_enhanced_prompt']
