# TokenScam Shield

AI-powered weekly intelligence brief tracking crypto token scams, rug pulls, honeypot tokens, pump-and-dump schemes, and Ponzi schemes across multiple blockchain networks.

## What It Does

TokenScam Shield monitors the crypto token landscape for scam signals and produces actionable intelligence for investors, researchers, and compliance teams.

**Data pipeline:**
1. **Multi-query fetch** from [CPW Tracker API](https://rapidapi.com/CPWatch/api/cpw-tracker) covering 5 scam categories (token scams, fraud, rug pulls, Ponzi schemes, pump-and-dumps)
2. **Deduplication and enrichment** with scam type classification and source extraction
3. **AI severity analysis** via [GitHub Models](https://docs.github.com/en/github-models) (GPT-4o-mini) assigning risk scores, severity ratings, attack vectors, and impact estimates
4. **Weekly intelligence brief** generation with trend analysis and actionable recommendations
5. **Interactive dashboard** deployed to GitHub Pages with filtering, charts, and share buttons

## How It Differs from the Template

| Aspect | Product Kit Template | TokenScam Shield |
|--------|---------------------|-----------------|
| Queries | Single API call | 5 specialized queries with deduplication |
| Domain | Generic event monitoring | Token-specific scam intelligence |
| Processing | Raw JSON storage | Scam classification, source extraction, merge history |
| AI Layer | None | 2-pass analysis (severity scoring + intelligence brief) |
| History | Overwrite | Rolling merge, 300-event cap, 52-week archive |
| Frontend | None | Full interactive dashboard with filters and charts |

## Setup

1. **Clone this repository**
2. **Subscribe to API**: Go to [CPW API](https://rapidapi.com/CPWatch/api/cpw-tracker) and subscribe to the Basic plan
3. **Add secrets** in Settings > Secrets > Actions:
   - `RAPIDAPI_KEY` — your CPW Tracker API key
   - `GITHUB_TOKEN` — automatically provided by GitHub Actions
4. **Run the workflow** manually or wait for the weekly schedule (Sundays at 10:00 UTC)

## Local Development

```bash
# Fetch fresh data
RAPIDAPI_KEY=your_key node scripts/api-call.js

# Run AI analysis
GITHUB_TOKEN=your_token node scripts/ai-analysis.js

# Open the dashboard
open index.html
```

## Project Structure

```
token-scam-shield/
  scripts/
    api-call.js        # Multi-query data pipeline with dedup and classification
    ai-analysis.js     # AI severity scoring and intelligence brief generation
  data/
    events.json        # Enriched scam events (auto-updated)
    analysis.json      # Weekly intelligence brief (auto-updated)
    history.json       # Rolling 52-week archive
  .github/
    workflows/
      deploy.yml       # Weekly automation + GitHub Pages deployment
  index.html           # Interactive dashboard (zero dependencies)
  package.json
  README.md
```

## Scam Categories Tracked

- **Rug pulls** — Liquidity drain events on DEXes
- **Honeypot tokens** — Contracts that prevent selling
- **Pump-and-dump** — Coordinated price manipulation
- **Ponzi schemes** — Unsustainable yield platforms
- **Exit scams** — Fake projects that disappear with presale funds
- **Phishing** — Fake airdrops and wallet drainers
- **General fraud** — Hidden admin functions, unlimited mints, etc.

## Use Cases

- **Retail investors** checking token safety before buying
- **Security researchers** tracking scam patterns and attack vectors
- **Compliance teams** monitoring token fraud activity
- **Educators** demonstrating real-world scam mechanics to students

## Built With

- [Product Kit Template](https://github.com/1712n/product-kit-template)
- [CPW Tracker API](https://rapidapi.com/CPWatch/api/cpw-tracker)
- [GitHub Models](https://docs.github.com/en/github-models) (GPT-4o-mini)
- GitHub Actions + GitHub Pages
