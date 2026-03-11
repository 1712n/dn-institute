# Market Health Reporter

Automatically generates market health reports with metrics spike analysis using the [Market Health API](https://dn.institute/market-health/docs/market-health-metrics/) and OpenAI GPT-4.

## Features

- Fetches market metrics from the Cross-Market Surveillance API
- Generates structured markdown reports with spike interpretation
- **RAG (Retrieval Augmented Generation)**: enriches report context with real-time crypto news from [CryptoPanic](https://cryptopanic.com/developers/api/) and [NewsAPI](https://newsapi.org/)
- Keyword-based semantic retrieval selects the most relevant articles for each market venue and trading pair
- Publishes generated reports as GitHub issue comments

## Usage

```bash
python -m tools.market_health_reporter.market_health_reporter \
  --llm-api-key <OPENAI_API_KEY> \
  --issue <ISSUE_NUMBER> \
  --comment-body "pair:<PAIRID>, <MARKETVENUEID>, <START_DATE>, <END_DATE>" \
  --github-token <GITHUB_TOKEN> \
  --rapid-api <RAPIDAPI_KEY> \
  --cryptopanic-api-key <CRYPTOPANIC_API_KEY> \
  --newsapi-key <NEWSAPI_KEY>
```

## RAG Methodology

1. **Fetch**: Retrieve up to 5 articles each from CryptoPanic and NewsAPI, filtered by the trading pair currency and market venue.
2. **Extract**: Pull plain text from article HTML using BeautifulSoup, stripping navigation, scripts, and boilerplate.
3. **Retrieve**: Score articles by keyword overlap with the market venue and trading pair; select the top 3 most relevant.
4. **Augment**: Inject the retrieved article snippets into the LLM prompt as a `<context>` block, capped at 8,000 tokens to stay within the model's context window.

## Environment Variables (optional)

| Variable | Description |
|---|---|
| `CRYPTOPANIC_API_KEY` | Free API key from [CryptoPanic](https://cryptopanic.com/developers/api/) |
| `NEWSAPI_KEY` | Free API key from [NewsAPI](https://newsapi.org/) |

Both keys are optional. If omitted, the reporter falls back to generating reports from market data alone.

## Dependencies

- `openai`
- `tiktoken`
- `requests`
- `beautifulsoup4`
- `PyGithub`
