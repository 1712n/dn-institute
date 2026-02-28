# 🌰 Article Checker Worker

A Cloudflare Worker that fact-checks articles submitted via pull requests using Claude and Brave Search. Replaces the Python-based GitHub Action (`article-check-claude.yml`) with a lightweight, webhook-driven serverless worker.

## Architecture

```
GitHub PR comment (/articlecheck)
  → Webhook POST to CF Worker
  → HMAC-SHA256 signature verification
  → Reviewer allowlist gate
  → Respond 200 immediately (waitUntil for async processing)
  → Phase 1: Extract factual statements (Claude)
  → Phase 2: Iterative fact-checking via Brave Search (up to 5 rounds)
  → Phase 3: Comprehensive review (fact-checks + editor notes + Hugo SSG + metadata)
  → Post review as PR comment
```

**Single-worker design**: Uses `waitUntil()` for background processing. No Queues, Durable Objects, or multi-worker patterns. Fetch wait time does not count toward the 30-second CPU limit.

## File Structure

```
article_checker_worker/
├── src/
│   ├── index.ts        # Hono app, webhook routing, main handler
│   ├── types.ts        # TypeScript type definitions
│   ├── crypto.ts       # HMAC-SHA256 signature verification (Web Crypto API)
│   ├── github.ts       # PR diff fetch, comment posting, allowlist
│   ├── pipeline.ts     # 3-phase pipeline (extract → verify → review)
│   ├── llm.ts          # Claude Messages API client
│   └── search.ts       # Brave Search API client
├── test/
│   ├── crypto.spec.ts  # Signature verification tests
│   ├── github.spec.ts  # GitHub interaction tests
│   ├── pipeline.spec.ts# Pipeline helper tests
│   ├── search.spec.ts  # Search formatting tests
│   └── index.spec.ts   # Webhook routing integration tests
├── package.json
├── tsconfig.json
├── vitest.config.ts
├── wrangler.toml
└── README.md
```

## Setup

### Prerequisites

- [Node.js](https://nodejs.org/) >= 18
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- A Cloudflare account

### Install Dependencies

```bash
cd tools/article_checker_worker
npm install
```

### Configure Secrets

Set the required secrets using Wrangler:

```bash
wrangler secret put WEBHOOK_SECRET    # GitHub webhook secret
wrangler secret put GITHUB_TOKEN      # GitHub PAT with repo scope
wrangler secret put ANTHROPIC_API_KEY # Claude API key
wrangler secret put BRAVE_API_KEY     # Brave Search API key
```

Optionally set the reviewer allowlist as a variable:

```bash
# In wrangler.toml or via dashboard
# REVIEWER_ALLOWLIST = '["evgenydmitriev","reviewer2"]'
```

If not set, defaults to `["evgenydmitriev"]`.

### Deploy

```bash
npm run deploy
```

### Configure GitHub Webhook

1. Go to your repo's **Settings → Webhooks → Add webhook**
2. **Payload URL**: `https://article_checker_worker.<your-subdomain>.workers.dev/webhook`
3. **Content type**: `application/json`
4. **Secret**: Same value as `WEBHOOK_SECRET`
5. **Events**: Select "Issue comments"

### Disable Legacy Workflow

Once the worker is deployed and verified, disable the GitHub Action:

```yaml
# .github/workflows/article-check-claude.yml
# Add at the top of the file:
# name: Article Check (Legacy - Disabled)
# on: workflow_dispatch  # Disable automatic triggers
```

## Development

```bash
# Local development
npm run dev

# Run tests
npm test
```

## Testing

```bash
npm test
```

Tests cover:
- HMAC-SHA256 signature verification (valid, invalid, missing, tampered)
- Reviewer allowlist (defaults, custom JSON, invalid JSON)
- Webhook payload validation (PR comments, non-PR comments, missing trigger)
- Diff parsing (single file, multiple files, non-markdown filtering)
- Pipeline helpers (tag extraction, multiline, edge cases)
- Search result formatting (XML structure, indices, empty results)
- Webhook routing integration (auth, filtering, allowlist)

## Pipeline Details

### Phase 1: Statement Extraction

Claude extracts key factual statements (dates, numbers, names, organizations) from the article text.

### Phase 2: Iterative Fact-Checking

For each statement, Claude formulates a search query. The worker executes the query against Brave Search and feeds results back. This continues iteratively (up to 5 rounds) until all statements have verdicts.

### Phase 3: Comprehensive Review

Claude generates a final review including:
- **Fact-checking results** with ✅/❌/⚠️ verdicts and sources
- **Editor's notes** on grammar, style, and timeline formatting
- **Hugo SSG formatting check**
- **Filename validation** (YYYY-MM-DD-entity.md convention)
- **Section headers check** (Summary, Attackers, Losses, Timeline, Security Failure Causes)
- **Metadata headers check** (date, target-entities, entity-types, attack-types, title, loss)

## Security

- **HMAC-SHA256 verification** with constant-time comparison (prevents timing attacks)
- **Reviewer allowlist** prevents unauthorized trigger
- **No secrets in code** — all credentials via Wrangler secrets
- **Immediate 200 response** — background processing via `waitUntil()`
