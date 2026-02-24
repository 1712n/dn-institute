# QA Bot — Cloudflare Worker

Serverless article quality checker for the [Crypto Attack Wiki](https://github.com/1712n/dn-institute/tree/main/content/attacks). Migrated from the [GitHub Actions workflow](https://github.com/1712n/dn-institute/blob/main/.github/workflows/article-check-claude.yml) to a webhook-based Cloudflare Worker.

## Architecture

```
GitHub webhook → Cloudflare Worker → Claude API + Brave Search → GitHub PR comment
```

### 3-Phase Pipeline (feature parity with Python bot)

1. **Statement Extraction** (Claude Haiku) — extracts key factual claims from the article
2. **Iterative Fact Verification** (Claude Sonnet + Brave Search) — searches the web to verify each statement, up to 5 search iterations
3. **Comprehensive Review** (Claude Sonnet) — generates the final review including:
   - Fact-checking results with sources
   - Editor's notes (grammar, style, timeline formatting)
   - Hugo SSG formatting validation
   - Metadata headers & filename compliance check

### Trigger Methods

| Trigger | Event | Description |
|---------|-------|-------------|
| `/articlecheck` comment | `issue_comment` | Manual trigger by authorized reviewer (same as legacy bot) |
| PR opened/updated | `pull_request` | Automatic check on new or updated PRs |

## Setup

### 1. Deploy

```bash
cd workers/qa-bot
npm install
npx wrangler deploy
```

### 2. Configure Secrets

```bash
npx wrangler secret put GITHUB_WEBHOOK_SECRET
npx wrangler secret put GITHUB_TOKEN
npx wrangler secret put LLM_API_KEY
npx wrangler secret put SEARCH_API_KEY
npx wrangler secret put WIKI_REVIEWERS   # e.g. '["evgenydmitriev","reviewer2"]'
```

### 3. Register GitHub Webhook

In your repo settings → Webhooks → Add webhook:
- **Payload URL**: `https://qa-bot.<your-subdomain>.workers.dev/webhook`
- **Content type**: `application/json`
- **Secret**: Same value as `GITHUB_WEBHOOK_SECRET`
- **Events**: Select `Issue comments` and `Pull requests`

## Development

```bash
npm install
npm run dev     # local dev server with wrangler
npm test        # run vitest tests
```

## Security

- Webhook signatures verified with HMAC-SHA256 (constant-time comparison)
- Only users listed in `WIKI_REVIEWERS` can trigger manual `/articlecheck`
- All API keys stored as Cloudflare Worker secrets (never in code)

## Improvements over GitHub Actions

| Aspect | GitHub Actions | Cloudflare Worker |
|--------|---------------|-------------------|
| Cold start | ~30s (Python + poetry install) | <5ms |
| Trigger | Polling-based workflow | Real-time webhook |
| Cost | GitHub Actions minutes | CF free tier (100k req/day) |
| Runtime | Ubuntu VM per run | V8 isolate (lightweight) |
| Dependencies | Python + poetry + pip packages | Zero runtime deps (fetch only) |
