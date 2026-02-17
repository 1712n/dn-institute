# QA Bot — Cloudflare Worker

A Cloudflare Worker that replaces the GitHub Actions-based article quality checker. It receives GitHub webhook events for pull requests, checks article content against [submission guidelines](https://github.com/1712n/dn-institute/issues/277), and posts review comments with fact-checking results, editor's notes, and formatting validation.

## Architecture

```
GitHub Webhook ──> Cloudflare Worker ──> Claude API (fact extraction + verification)
                       │                      │
                       │                      └──> Brave Search API (source verification)
                       │
                       └──> GitHub API (post review comment)
```

**Trigger modes:**

1. **Comment-triggered** (`/articlecheck` command) — same as the original bot. Only users listed in `WIKI_REVIEWERS` can trigger checks.
2. **Automatic** — triggers on `pull_request` `opened` / `synchronize` events for immediate feedback.

## Setup

### 1. Deploy the Worker

```bash
cd workers/qa-bot
npm install
npx wrangler deploy
```

### 2. Configure Secrets

```bash
npx wrangler secret put GITHUB_TOKEN          # GitHub PAT with repo access
npx wrangler secret put ANTHROPIC_API_KEY      # Anthropic API key
npx wrangler secret put BRAVE_API_KEY          # Brave Search API key
npx wrangler secret put GITHUB_WEBHOOK_SECRET  # Webhook secret (you create this)
npx wrangler secret put WIKI_REVIEWERS         # Comma-separated GitHub usernames
```

### 3. Configure GitHub Webhook

In your repository settings (**Settings > Webhooks > Add webhook**):

| Field | Value |
|-------|-------|
| Payload URL | `https://dn-institute-qa-bot.<your-subdomain>.workers.dev` |
| Content type | `application/json` |
| Secret | Same value as `GITHUB_WEBHOOK_SECRET` |
| Events | Select: **Issue comments**, **Pull requests** |

### 4. (Optional) Disable the GitHub Actions Workflow

Once the Worker is deployed and verified, you can disable the old workflow:

```bash
gh workflow disable article-check-claude.yml
```

## How It Works

The Worker mirrors the original Python bot's three-phase Claude pipeline:

1. **Statement Extraction** — Claude (Haiku, for speed) extracts key factual claims from the article.
2. **Search & Verification** — Claude (Sonnet) iteratively searches via Brave and verifies each statement.
3. **Final Review** — Claude generates a comprehensive review covering:
   - Fact-checking results with sources
   - Editor's notes (grammar, style)
   - Hugo SSG formatting compliance
   - Submission guidelines compliance (filename, headers, metadata)

## Key Differences from GitHub Actions Version

| Aspect | GitHub Actions | Cloudflare Worker |
|--------|---------------|-------------------|
| Runtime | Python + Poetry | TypeScript (no dependencies) |
| Trigger | Issue comment only | Webhook (comment + PR events) |
| Cold start | ~30s (install deps) | <5ms |
| Cost | GitHub Actions minutes | Cloudflare Workers free tier (100k req/day) |
| Security | GitHub secrets | Wrangler secrets + HMAC webhook verification |
| Dependencies | anthropic SDK, PyGithub, requests, etc. | Zero external dependencies (fetch API only) |

## Development

```bash
npm install
npm run dev    # Local dev server with wrangler
npm run test   # Run tests
```

## Security

- All webhook payloads are verified with HMAC-SHA256 signatures.
- API keys are stored as Cloudflare Worker secrets (encrypted at rest).
- The `/articlecheck` command requires the commenter to be in the `WIKI_REVIEWERS` allowlist.
- No external dependencies — reduces supply chain attack surface.
