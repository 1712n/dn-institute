# WashWatch - Crypto Market Manipulation Intelligence

AI-powered detection and monitoring of wash trading, spoofing, pump-and-dump schemes, and other market manipulation patterns in cryptocurrency markets.

**[Live Dashboard](https://elromevedelelyon.github.io/washwatch/)** | Built on [Product Kit Template](https://github.com/1712n/product-kit-template)

## What It Does

WashWatch continuously monitors cryptocurrency markets for manipulation signals across four categories:

- **Wash Trading** - Artificial volume inflation through self-dealing trades
- **Spoofing & Layering** - Fake orders placed and cancelled to mislead the market
- **Pump & Dump** - Coordinated price inflation followed by mass selling
- **Market Manipulation** - MEV extraction, sandwich attacks, and other manipulation tactics

### Key Features

- Weekly automated data collection from [CPW API](https://rapidapi.com/CPWatch/api/cpw-tracker)
- AI-enhanced analysis using [GitHub Models](https://docs.github.com/en/github-models) (GPT-4o-mini)
- Severity classification (Critical / High / Medium / Low)
- Entity extraction identifying affected exchanges and protocols
- Rolling 90-day signal database with deduplication
- Interactive dashboard with threat assessment and recommendations
- Share alerts directly to X/Twitter

## Detection Methodology

WashWatch leverages DN Institute's market health research methodologies:

| Method | Description |
|--------|-------------|
| **Benford's Law** | Tests first-digit distribution of trade values against natural distribution |
| **Buy/Sell Ratio** | Detects extreme volume imbalances indicating coordinated activity |
| **Volume Distribution** | Identifies round-number clustering typical of wash trades |
| **Time-of-Trade** | Finds temporal clustering suggesting automated manipulation |
| **VWAP Deviation** | Spots artificial price movements disconnected from market activity |
| **AI Correlation** | Cross-references signals across venues to identify campaigns |

For detailed methodology, see the [DN Institute Market Health API docs](https://rapidapi.com/DNInstitute/api/crypto-market-health).

## Setup

1. **Clone this repo** (or use as template)
2. **Subscribe to API**: Go to [CPW API](https://rapidapi.com/CPWatch/api/cpw-tracker) and subscribe to the Basic plan (100 free requests/month)
3. **Add secrets** in Settings > Secrets > Actions:
   - `RAPIDAPI_KEY` - Your CPW API key
   - `GITHUB_TOKEN` is automatically available for GitHub Models AI analysis
4. **Enable GitHub Pages**: Settings > Pages > Source: GitHub Actions
5. **Run the workflow**: Actions > WashWatch Deploy > Run workflow

## Architecture

```
washwatch/
├── .github/workflows/deploy.yml   # Automated weekly updates + GitHub Pages deploy
├── scripts/
│   ├── api-call.js                # CPW API data fetcher (4 manipulation categories)
│   └── ai-analyze.js              # GitHub Models AI analysis (with rule-based fallback)
├── data/
│   ├── signals.json               # Rolling 90-day signal database
│   ├── stats.json                 # Aggregate statistics
│   └── analysis.json              # AI-generated intelligence brief
├── index.html                     # Interactive dashboard (GitHub Pages)
├── package.json
└── README.md
```

## Data Flow

1. **Fetch** - `api-call.js` queries CPW API for 4 manipulation categories (wash trading, market manipulation, spoofing, pump-and-dump)
2. **Enrich** - Each signal is classified by severity, entities are extracted, metadata is added
3. **Store** - Signals are merged with existing database, deduplicated, and trimmed to 90-day window
4. **Analyze** - `ai-analyze.js` generates an intelligence brief using GitHub Models AI (falls back to rule-based analysis)
5. **Display** - `index.html` renders the dashboard from JSON data files
6. **Repeat** - GitHub Actions runs weekly on Sunday at 12:00 UTC

## Data Sources

- **[CPW API](https://rapidapi.com/CPWatch/api/cpw-tracker)** - Catastrophic event and market intelligence tracking
- **[DN Institute Market Health API](https://rapidapi.com/DNInstitute/api/crypto-market-health)** - Statistical market surveillance metrics
- **[GitHub Models](https://docs.github.com/en/github-models)** - AI analysis (GPT-4o-mini, free with GitHub account)

## Customization

### Change detection parameters

Edit `scripts/api-call.js` to modify:
- Time range (default: 7 days, max: 7 days)
- Entity types to monitor
- Manipulation categories to track
- Severity classification rules

### Change AI analysis

Edit `scripts/ai-analyze.js` to modify:
- Analysis prompt and output format
- Model selection (default: gpt-4o-mini)
- Rule-based fallback logic

## Contributing

This project is part of the [DN Institute Challenge Program](https://github.com/1712n/dn-institute#-challenge-program). Contributions welcome via pull request.

## License

MIT
