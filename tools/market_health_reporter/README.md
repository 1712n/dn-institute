# Market Health Reporter

Automatically generates market health reports with metric spike analysis using the [Market Health API](https://dn.institute/market-health/docs/market-health-metrics/).

## Features

- Fetches market metrics from the Cross-Market Surveillance API
- Generates structured markdown reports aligned with [contribution guidelines](https://github.com/1712n/dn-institute/issues/277)
- **RAG (Retrieval Augmented Generation)**: enriches reports with real-time context from external crypto news sources

## RAG Integration

The reporter optionally fetches recent articles from:

- **[CryptoPanic](https://cryptopanic.com/developers/api/)** – crypto-specific news aggregator (free tier available)
- **[NewsAPI](https://newsapi.org/)** – general news aggregator (free tier available)

Articles are embedded using OpenAI's `text-embedding-ada-002` model. Cosine similarity is used to select the most relevant articles for the given market venue, trading pair, and time window. The top articles are injected into the LLM prompt as additional context, improving alignment with the target article structure and contribution guidelines.

## Usage

```bash
python -m tools.market_health_reporter.market_health_reporter \
  --llm-api-key "<OPENAI_API_KEY>" \
  --issue "<GITHUB_ISSUE_NUMBER>" \
  --comment-body "pair:<PAIRID>, <MARKETVENUEID>, <START_DATE>, <END_DATE>" \
  --github-token "<GITHUB_TOKEN>" \
  --rapid-api "<RAPIDAPI_KEY>" \
  --cryptopanic-api-key "<CRYPTOPANIC_KEY>" \
  --newsapi-key "<NEWSAPI_KEY>"
```

The `--cryptopanic-api-key` and `--newsapi-key` arguments are optional. When omitted, the reporter falls back to generating the report without external context.

## Dependencies

```
openai
tiktoken
requests
numpy
PyGithub
```
