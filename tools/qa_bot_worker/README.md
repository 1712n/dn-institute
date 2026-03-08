# QA Bot Worker

A Cloudflare Worker that automates article quality checks for the [dn-institute](https://github.com/1712n/dn-institute) Crypto Attack Wiki. Migrated from the [GitHub Actions workflow](../../.github/workflows/article-check-claude.yml) to a webhook-based serverless architecture.

## Architecture

```
GitHub PR event ─┐
                 ├─→ GitHub Webhook ─→ CF Worker ─→ Claude API ─→ PR Comment
PR comment ──────┘                         │
                                           └─→ Brave Search API
```

### Trigger Modes

| Trigger | Event | Condition |
|---------|-------|-----------|
| Auto | `pull_request` opened/synchronized | Runs on every new/updated PR |
| Manual | `issue_comment` created | Comment contains `/articlecheck` |

## Analysis Pipeline

1. **Extract statements** — Claude extracts factual claims from the article
2. **Fact-check via search** — iterative retrieval loop: Claude formulates queries → Brave Search returns results → Claude verifies
3. **Editorial review** — Claude produces a comprehensive review covering:
   - Fact-checking results with sources
   - Editor's notes (grammar, style)
   - Hugo SSG formatting compliance
   - Filename & metadata validation

## Setup

### 1. Install dependencies

```bash
cd tools/qa_bot_worker
npm install
```

### 2. Configure secrets

```bash
wrangler secret put GITHUB_TOKEN          # GitHub PAT with repo + PR permissions
wrangler secret put ANTHROPIC_API_KEY     # Anthropic API key
wrangler secret put GITHUB_WEBHOOK_SECRET # Secret for webhook signature verification
wrangler secret put BRAVE_API_KEY         # Brave Search API key
```

### 3. Deploy

```bash
npm run deploy
```

### 4. Configure GitHub Webhook

1. Go to **Repository Settings → Webhooks → Add webhook**
2. **Payload URL:** `https://qa-bot-worker.<your-subdomain>.workers.dev/webhook`
3. **Content type:** `application/json`
4. **Secret:** Same value as `GITHUB_WEBHOOK_SECRET`
5. **Events:** Select `Pull requests` and `Issue comments`

## Development

```bash
npm run dev    # Start local dev server with wrangler
npm run test   # Run tests with vitest
```

## Comparison: GHA vs CF Worker

| Aspect | GitHub Actions (current) | CF Worker (new) |
|--------|------------------------|-----------------|
| Trigger | `/articlecheck` comment only | PR events + `/articlecheck` |
| Cold start | ~30s (VM spin-up + poetry install) | <50ms |
| Runtime | Python + Poetry | TypeScript (Hono) |
| LLM | Claude (Anthropic Python SDK) | Claude (Anthropic REST API) |
| Search | Brave (Python) | Brave (fetch) |
| Cost | GitHub Actions minutes | CF Workers free tier (100k req/day) |
| Security | GitHub Secrets | Wrangler Secrets + HMAC webhook verification |

## Fallback

The original GitHub Actions workflow (`.github/workflows/article-check-claude.yml`) is preserved as a fallback. Both systems can coexist — the GHA triggers on `/articlecheck` comments while the Worker can additionally auto-trigger on PR events.
