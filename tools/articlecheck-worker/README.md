# Article Check Worker

Cloudflare Worker that migrates the `/articlecheck` QA bot from GitHub Actions to a webhook-based serverless architecture.

## Architecture

Single Worker with two handlers: a `fetch` handler (webhook receiver) and a `queue` handler (pipeline processor).

```
GitHub PR Comment (/articlecheck)
  → Webhook POST to Worker fetch handler
  → Verify HMAC-SHA256 signature (timing-safe)
  → Check reviewer permissions
  → Dedup via KV (prevent reprocessing)
  → Enqueue job to Cloudflare Queue
  → Respond 202 Accepted (<10ms)

Queue Consumer (15 min wall clock budget)
  → Fetch PR diff from GitHub API
  → Phase 1: Extract factual statements (Claude Opus)
  → Phase 2: Fact-check loop (Brave Search + HTMLRewriter scraping + Claude Haiku summarization + Claude Opus verification)
  → Phase 3: Editorial review (Claude Opus)
  → Post review comment on PR
```

### Why a Queue instead of `waitUntil()`?

`ctx.waitUntil()` has a **hard 30-second limit** after the response is sent. The 3-phase pipeline with Claude API calls, Brave searches, page scraping, and Haiku summarization needs 60-180 seconds. Queue consumers get **15 minutes** of wall clock time — more than enough, with automatic retry on failure.

### 3-Phase AI Pipeline (preserved from Python original)

1. **Extract Statements** — Claude extracts factual claims (dates, dollar amounts, entity names) from the article
2. **Fact-Check Loop** — For each statement:
   - Claude generates a search query
   - Brave Search API returns ranked results (using `mixed.main` ordering for web/news/FAQ interleaving)
   - Web pages are scraped using **HTMLRewriter** (Cloudflare's native streaming HTML parser — the Workers equivalent of BeautifulSoup)
   - Scraped content is summarized by **Claude Haiku** for focused article extraction
   - Claude Opus verifies the statement as True/False/Unverified with sources
3. **Editorial Review** — Claude produces a comprehensive review: fact-check results with sources, editor's notes, Hugo SSG formatting check, filename validation, metadata header validation

### Key Implementation Details

| Feature | Python Original | This Worker |
|---------|----------------|-------------|
| HTML parsing | BeautifulSoup + bleach | HTMLRewriter (Cloudflare native) |
| Page summarization | Claude Haiku (claude-3-haiku) | Claude Haiku (same model, same params) |
| Search result ordering | Brave `mixed.main` ranked interleave | Brave `mixed.main` ranked interleave |
| FAQ results | Parsed and included | Parsed and included |
| n_search_results_to_use | 1 | 1 |
| max_searches_to_try | 5 | 5 |
| Retry logic | tenacity (10 attempts, exp backoff) | Custom (10 attempts, exp backoff, same delays) |
| RETRIEVAL_PROMPT {description} | Dynamic from search_tool.tool_description | Dynamic from BRAVE_DESCRIPTION constant |
| Signature verification | N/A (GitHub Actions) | HMAC-SHA256 timing-safe comparison |
| Idempotency | None | KV-backed dedup on delivery ID |
| Duplicate comment detection | None | Checks for HTML marker |
| Error handling | Prints to stdout | Posts sanitized error to PR (secrets redacted) |
| Background processing | N/A (runs synchronously) | Cloudflare Queue (15 min wall clock, auto-retry) |

## Setup

### Prerequisites

- [Cloudflare account](https://dash.cloudflare.com/) (Workers Paid plan required for Queues)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
- GitHub personal access token with `repo` scope
- [Anthropic API key](https://console.anthropic.com/)
- [Brave Search API key](https://brave.com/search/api/)

### 1. Create KV namespace and Queue

```bash
wrangler kv namespace create DEDUP_KV
wrangler queues create articlecheck-pipeline
```

Update `wrangler.toml` with the returned KV namespace ID.

### 2. Set secrets

```bash
wrangler secret put GITHUB_WEBHOOK_SECRET
wrangler secret put GITHUB_TOKEN
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put BRAVE_API_KEY
wrangler secret put WIKI_REVIEWERS  # JSON array: '["evgenydmitriev","reviewer2"]'
```

Optional model overrides:
```bash
wrangler secret put ANTHROPIC_MODEL          # default: claude-3-opus-20240229
wrangler secret put ANTHROPIC_MAX_TOKENS     # default: 4000
```

### 3. Deploy

```bash
cd workers/articlecheck
npm install
npm run deploy
```

### 4. Configure GitHub webhook

In repo Settings → Webhooks:

- **Payload URL**: `https://articlecheck.<subdomain>.workers.dev`
- **Content type**: `application/json`
- **Secret**: Same value as `GITHUB_WEBHOOK_SECRET`
- **Events**: Select "Issue comments"

### 5. Disable the old GitHub Actions workflow

This PR changes the legacy `article-check-claude.yml` trigger to `workflow_dispatch` only (manual), so it won't run on `/articlecheck` comments anymore. The duplication-check and plagiarism-check workflows are unaffected.

## Development

```bash
npm install
npm run dev        # Local dev server
npm test           # Run all tests (74 tests)
npm run typecheck  # TypeScript strict mode check
```

## File Structure

```
src/
  index.ts      — fetch handler (webhook) + queue handler (pipeline consumer)
  github.ts     — Signature verification, diff fetching/parsing, PR commenting
  pipeline.ts   — 3-phase Claude AI pipeline (extract → fact-check → review)
  brave.ts      — Brave Search with HTMLRewriter scraping + Claude Haiku summarization
  prompts.ts    — All Claude prompts (preserved verbatim from Python)
  types.ts      — TypeScript interfaces
test/
  github.test.ts      — 31 unit tests for GitHub utilities + tag extraction
  brave.test.ts       — 7 unit tests for search formatting + description matching
  simulation.test.ts  — 36 E2E simulation + adversarial tests
```

## Resource Usage Per Review

| Resource | Count | Notes |
|----------|-------|-------|
| Claude Opus API calls | 3-8 | 1 extract + 1-5 fact-check + 1 editorial |
| Claude Haiku API calls | 1-5 | 1 per scraped web page (summarization) |
| Brave Search API calls | 1-5 | 1 per fact-checked statement |
| Web page fetches | 1-5 | 1 per search query (n_search_results_to_use=1) |
| Estimated wall clock | 60-180s | Well within Queue's 15-minute limit |
| KV operations | 2 | 1 get + 1 put for dedup |
| Queue messages | 1 | 1 per webhook |
| Bundle size | 36 KiB gzip | Single worker |
