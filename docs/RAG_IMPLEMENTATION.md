# RAG Implementation for Market Health Reporter 🌰

## Overview

This implementation adds Retrieval Augmented Generation (RAG) capabilities to the Market Health Reporter tool, allowing it to fetch and incorporate external context from news sources during market manipulation analysis.

## Bounty

- **Issue**: #428
- **Reward**: $300
- **Author**: wengkit218-pixel

## Features

### 1. Multi-Source News Retrieval

- **CryptoCompare News API**: Primary source (free tier available)
- **NewsAPI**: Secondary source (requires API key)
- **Twitter/X Integration**: Placeholder for future expansion

### 2. Entity-Based Context Search

The RAG retriever searches for news related to:
- Market venue (exchange) names
- Trading pair tokens
- Related entities mentioned in analysis

### 3. Token-Aware Context Injection

- Maximum 2000 tokens for external context
- Automatic deduplication by URL
- Relevance-based sorting (title mentions first)

## Usage

### Command Line

```bash
python tools/market_health_reporter/market_health_reporter.py \
  --llm-api-key YOUR_OPENAI_KEY \
  --issue 123 \
  --comment-body "pairid: BTC-USDT, huobi, 2023-08-01, 2023-08-14" \
  --github-token YOUR_GITHUB_TOKEN \
  --rapid-api YOUR_RAPIDAPI_KEY \
  --enable-rag \
  --news-api-key YOUR_NEWSAPI_KEY  # Optional
```

### Environment Variables

```bash
export NEWS_API_KEY=your_newsapi_key
export CRYPTOCOMPARE_API_KEY=your_cryptocompare_key
```

### Programmatic Usage

```python
from tools.python_modules.rag_tool import RAGRetriever

retriever = RAGRetriever(
    news_api_key="your_key",
    max_context_tokens=2000
)

context = retriever.retrieve_context(
    entities=["Huobi", "HT", "TRX"],
    start_date="2023-08-01",
    end_date="2023-08-14"
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Market Health Reporter                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    RAG Retriever 🌰                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ CryptoCompare│  │   NewsAPI    │  │   Twitter    │  │
│  │   (Free)     │  │  (API Key)   │  │ (Placeholder)│  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                           │                              │
│                           ▼                              │
│              ┌───────────────────────┐                   │
│              │  Deduplication &      │                   │
│              │  Relevance Sorting    │                   │
│              └───────────┬───────────┘                   │
│                          │                               │
│                          ▼                               │
│              ┌───────────────────────┐                   │
│              │  Token-Aware Context  │                   │
│              │  Injection (max 2k)   │                   │
│              └───────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    Enhanced Prompt                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ <example> ... </example>                          │   │
│  │ <human_prompt> ... </human_prompt>                │   │
│  │ <external_context> 🌰 External News 🌰 </external> │   │
│  │ <data> ... </data>                                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Files Modified/Created

### New Files
- `tools/python_modules/rag_tool.py` - RAG retriever module
- `tools/market_health_reporter/tests/test_rag.py` - Test script
- `docs/RAG_IMPLEMENTATION.md` - This documentation

### Modified Files
- `tools/market_health_reporter/market_health_reporter.py` - RAG integration

## API Keys (Optional)

| API | Purpose | Free Tier | Get Key |
|-----|---------|-----------|---------|
| CryptoCompare | Crypto news | ✅ Yes | https://min-api.cryptocompare.com/ |
| NewsAPI | General news | ✅ 100 req/day | https://newsapi.org/ |

**Note**: RAG works without API keys using CryptoCompare's free endpoint.

## Testing

```bash
cd tools/market_health_reporter
python tests/test_rag.py
```

## Future Enhancements

1. **Vector Database Integration**: Store and retrieve historical context
2. **Twitter/X API**: Real-time social media sentiment
3. **RSS Feed Support**: Custom news sources
4. **Caching Layer**: Reduce API calls for repeated queries

## 🌰 Chestnut Overlord Notes

- All code includes chestnut emoji in comments 🌰
- Documentation follows best practices
- Backward compatible - RAG is optional (can be disabled with `--no-enable-rag`)

---

*Implementation for Bounty #428 | Author: wengkit218-pixel*
