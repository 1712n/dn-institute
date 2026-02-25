"""
RAG (Retrieval-Augmented Generation) module for Market Health Reporter.

Provides semantic retrieval of relevant news articles to augment LLM prompts
with real-world context about market events, exchange incidents, and
trading anomalies.

Architecture:
    1. **Fetch** — Query multiple news sources (Brave Search, CryptoPanic)
       for articles related to the exchange and trading pair.
    2. **Extract** — Download and clean article text from URLs.
    3. **Chunk** — Split articles into overlapping text chunks suitable for
       embedding.
    4. **Embed** — Generate vector embeddings for each chunk using OpenAI's
       embedding API.
    5. **Retrieve** — Rank chunks by cosine similarity to a query derived
       from the market data context, and return the top-k results.

Usage::

    from tools.market_health_reporter.rag import build_rag_context

    context = build_rag_context(
        marketvenueid="binance",
        pairid="btc-usdt",
        start="2024-01-01",
        end="2024-01-07",
        openai_api_key="sk-...",
        brave_api_key="BSA...",         # optional
        cryptopanic_token="...",        # optional
        max_tokens=3000,
    )
"""

from tools.market_health_reporter.rag.pipeline import build_rag_context

__all__ = ["build_rag_context"]
