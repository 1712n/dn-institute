# RAG Module for Market Health Reporter 🌰

This module implements Retrieval Augmented Generation (RAG) for the Market Health Reporter, enabling it to fetch external news and market context to enhance report quality.

## Architecture 🌰

The RAG pipeline consists of 5 stages:

```
Sources → Extraction → Chunking → Retrieval → Formatting
```

### 1. Sources (`sources.py`)
Fetches news from multiple external APIs:
- **CryptoPanic API** - Crypto-focused news aggregator (API token optional)
- **NewsAPI** - General news with crypto filter (API key required)
- **DuckDuckGo** - Free web search fallback (no API key required)

### 2. Extraction (`extractor.py`)
Extracts clean text from HTML articles:
- BeautifulSoup-based parsing with multiple fallback strategies
- Removes navigation, ads, scripts, and boilerplate
- Caps content at configurable max chars per article

### 3. Chunking (`chunker.py`)
Splits text into semantic chunks:
- Sentence-aware chunking with overlap
- Preserves context across chunk boundaries
- Filters by relevance to exchange/pair being analyzed

### 4. Retrieval (`retriever.py`)
Semantic similarity search:
- **Primary**: OpenAI embeddings with cosine similarity
- **Fallback**: TF-IDF with cosine similarity (no API key required)

### 5. Formatting (`pipeline.py`)
Token-budget-aware context formatting:
- Clean, attributed context blocks
- XML-tagged injection into LLM prompt
- Source attribution with `[Source]` notation

## Usage 🌰

### Basic Usage (Free)

The RAG module works without any API keys using DuckDuckGo as the free source:

```bash
python tools/market_health_reporter/market_health_reporter.py \
  --llm-api-key $OPENAI_KEY \
  --issue 123 \
  --comment-body "pairid: btcusdt, huobi, 2024-01-01, 2024-01-07" \
  --github-token $GITHUB_TOKEN \
  --rapid-api $RAPID_API_KEY
```

### Enhanced Usage (with CryptoPanic)

For better crypto-focused news, provide a CryptoPanic API token:

```bash
python tools/market_health_reporter/market_health_reporter.py \
  --llm-api-key $OPENAI_KEY \
  --cryptopanic-token $CRYPTOPANIC_TOKEN \
  --issue 123 \
  --comment-body "pairid: btcusdt, huobi, 2024-01-01, 2024-01-07" \
  --github-token $GITHUB_TOKEN \
  --rapid-api $RAPID_API_KEY
```

### Disable RAG

To run without RAG (original behavior):

```bash
python tools/market_health_reporter/market_health_reporter.py \
  --no-rag \
  --llm-api-key $OPENAI_KEY \
  ...
```

## Configuration 🌰

| Argument | Default | Description |
|----------|---------|-------------|
| `--no-rag` | false | Disable RAG context retrieval |
| `--cryptopanic-token` | None | CryptoPanic API token |
| `--newsapi-key` | None | NewsAPI key |
| `--rag-max-context` | 3000 | Maximum context characters |

## Key Features 🌰

1. **Graceful Degradation**: If RAG fails, the reporter continues with standard behavior
2. **No Required Dependencies**: Works without any external API keys (uses DuckDuckGo)
3. **Relevance Filtering**: Only injects context relevant to the exchange/pair being analyzed
4. **Token Budget**: Respects configurable max context size
5. **Source Attribution**: All retrieved context includes source citations

## Dependencies 🌰

Required:
- `requests` (for HTTP requests)
- `openai` (for LLM calls, optional for embeddings)

Optional:
- `beautifulsoup4` (for better HTML extraction, falls back to regex if unavailable)

## Example Output 🌰

When RAG is enabled, the generated report includes:

```markdown
---
title: "Market Manipulation Analysis on Huobi"
date: 2024-01-01 - 2024-01-07
entities:
  - Huobi
  - BTC
---

## Summary

Analysis of BTC/USDT trading on Huobi reveals potential wash trading patterns...
[Cross-referenced with recent news about Huobi regulatory concerns [CoinDesk]]

---

*This report was enhanced with RAG context from external news sources. 🌰*
```

## Testing 🌰

Run tests:

```bash
python -m pytest tools/market_health_reporter/rag/tests/
```

## Files 🌰

```
rag/
├── __init__.py      # Module entry point
├── sources.py       # Multi-source news fetching
├── extractor.py     # HTML text extraction
├── chunker.py       # Sentence-aware chunking
├── retriever.py     # Semantic retrieval
├── pipeline.py      # End-to-end orchestrator
├── README.md        # This file
└── tests/
    └── test_rag.py  # Unit tests
```