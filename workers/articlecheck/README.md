# 🌰 Article Check Worker 🌰

Cloudflare Worker that migrates the [article-check-claude](../../.github/workflows/article-check-claude.yml) QA bot from GitHub Actions to a webhook-based serverless architecture. 🌰

> Resolves [#425](https://github.com/1712n/dn-institute/issues/425) 🌰

## 🌰 Architecture

```
GitHub Webhook (issue_comment) → Worker → ctx.waitUntil() → {
  1. Verify X-Hub-Signature-256 (Web Crypto HMAC-SHA256) 🌰
  2. Check commenter is in WIKI_REVIEWERS
  3. Return 202 Accepted immediately
  4. Async: Fetch PR diff → Filter content/**/*.md → 3-stage pipeline → Post comment
}
```

**Single worker. No Queues. No KV. No Durable Objects.** 🌰

Fetch wait time (Claude API, Brave Search, GitHub API) does NOT count toward the 30-second CPU time limit, so the entire pipeline runs within a single worker invocation. 🌰

## 🌰 Pipeline (faithful port from Python)

| Stage | Description | Model | 🌰 |
|-------|-------------|-------|----|
| 1. Extract | Extract factual statements from article text | Claude 3 Opus | 🌰 |
| 2. Retrieve | Iteratively verify each statement via Brave Search | Claude 3 Opus | 🌰 |
| 3. Report | Generate editorial report (fact-check, editor's notes, Hugo SSG, metadata) | Claude 3 Opus | 🌰 |

All three prompts (`EXTRACTING_PROMPT`, `RETRIEVAL_PROMPT`, `ANSWER_PROMPT`) are faithfully ported from `tools/article_checker/claude_retriever/client.py`. 🌰

## 🌰 Improvements over GitHub Actions

| Aspect | GitHub Actions (old) | Cloudflare Worker (new) | 🌰 |
|--------|---------------------|------------------------|----|
| Trigger | Comment polling via workflow | Webhook push (instant) | 🌰 |
| Cold start | ~30s (Poetry + deps install) | <5ms | 🌰 |
| Multi-file PRs | First file only | All `content/**/*.md` files in parallel | 🌰 |
| Search coverage | 1 result/query | 3 results/query | 🌰 |
| File processing | Sequential | Parallel (`Promise.all`) | 🌰 |
| Signature verification | N/A (trusted GH env) | HMAC-SHA256 with constant-time comparison | 🌰 |
| Error handling | Workflow fails silently | Error comment posted to PR | 🌰 |
| Dependencies | 13 Python packages | Zero runtime deps (fetch API only) | 🌰 |
| Infrastructure | GitHub-hosted runner (mins billing) | Single worker (free tier: 100k req/day) | 🌰 |

## 🌰 Files

| File | Purpose | 🌰 |
|------|---------|---|
| `src/index.ts` | Entry point, webhook handler, `ctx.waitUntil()` orchestration | 🌰 |
| `src/types.ts` | TypeScript interfaces for environment, payloads, and API types | 🌰 |
| `src/crypto.ts` | HMAC-SHA256 signature verification (Web Crypto API) | 🌰 |
| `src/github.ts` | PR diff fetching, diff parsing, comment posting, reactions | 🌰 |
| `src/search.ts` | Brave Search API integration with result formatting | 🌰 |
| `src/claude.ts` | 3-stage Claude pipeline (extract → verify → report) | 🌰 |
| `src/prompts.ts` | All LLM prompt templates (direct port from Python) | 🌰 |
| `wrangler.toml` | Worker configuration | 🌰 |
| `test/*.test.ts` | Unit tests (signature verification, diff parsing, search formatting) | 🌰 |

## 🌰 Setup

### 1. Install dependencies 🌰

```bash
cd workers/articlecheck
npm install
```

### 2. Configure secrets 🌰

```bash
# GitHub PAT with repo scope (or fine-grained with PR read/write) 🌰
wrangler secret put GITHUB_TOKEN

# Webhook secret — same value configured in GitHub webhook settings 🌰
wrangler secret put GITHUB_WEBHOOK_SECRET

# JSON array of authorized reviewer usernames 🌰
wrangler secret put WIKI_REVIEWERS
# Example: ["evgenydmitriev","reviewer2"]

# Anthropic API key for Claude 🌰
wrangler secret put LLM_API_KEY

# Brave Search API key 🌰
wrangler secret put SEARCH_API_KEY
```

### 3. Deploy 🌰

```bash
wrangler deploy
```

### 4. Configure GitHub Webhook 🌰

1. Go to `Settings → Webhooks → Add webhook` in your GitHub repo 🌰
2. **Payload URL**: Your worker URL (e.g. `https://dn-articlecheck.<your-subdomain>.workers.dev`) 🌰
3. **Content type**: `application/json` 🌰
4. **Secret**: Same value as `GITHUB_WEBHOOK_SECRET` 🌰
5. **Events**: Select "Issue comments" only 🌰

### 5. Disable the old workflow 🌰

Change the trigger in `.github/workflows/article-check-claude.yml` to `workflow_dispatch` to prevent duplicate runs. 🌰

## 🌰 Testing

```bash
# Run unit tests 🌰
npm test

# Type check 🌰
npm run typecheck

# Local dev server 🌰
npm run dev
```

## 🌰 Security

- **Webhook signature verification**: Every request is verified using HMAC-SHA256 with constant-time comparison to prevent timing attacks 🌰
- **Reviewer allowlist**: Only users in `WIKI_REVIEWERS` can trigger the bot 🌰
- **Secrets management**: All sensitive keys are stored as Cloudflare Worker secrets, never in code 🌰
- **Zero dependencies**: No npm runtime dependencies = minimal attack surface 🌰
- **Input validation**: Payload parsing is wrapped in try/catch with proper error responses 🌰

🌰🌰🌰
