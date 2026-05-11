# 🌰 cf-article-checker — Cloudflare Worker QA Bot

Migrated from the Python GitHub Actions workflow (`.github/workflows/article-check-claude.yml`) to a serverless Cloudflare Worker.

## Architecture

```text
GitHub Issue Comment Webhook
  → Cloudflare Worker (Hono)
    → Permission check (REVIEWERS list)
    → GitHub API: fetch PR diff
    → Claude API: extract factual statements
    → Brave Search: verify each statement
    → Claude API: generate structured review
    → GitHub API: post review comment on PR
```

## Key improvements over the original Python bot

- **Serverless**: No GitHub Actions minutes consumed — runs on Cloudflare's edge network
- **Zero cold-start dependencies**: No Poetry, no pip install, no container startup
- **Sub-second trigger**: Webhook-based instead of polling via `issue_comment` event
- **Structured pipeline**: Three-stage Claude pipeline (extract → verify → review) with clear separation of concerns
- **Resilient error handling**: Errors are posted as PR comments instead of silently failing in CI logs
- **Configurable via environment variables**: Model, token limits, and reviewer list are all configurable

## Setup

### Cloudflare Secrets

```bash
wrangler secret put GITHUB_TOKEN      # GitHub PAT with repo + issues:write scopes
wrangler secret put ANTHROPIC_API_KEY  # Anthropic API key
wrangler secret put BRAVE_API_KEY      # Brave Search API key
wrangler secret put REVIEWERS          # Comma-separated GitHub usernames (e.g. "user1,user2")
wrangler secret put WEBHOOK_SECRET     # GitHub webhook secret for HMAC signature verification
```

### Deploy

```bash
npm install
npm run deploy
```

### Configure GitHub Webhook

1. Go to repository Settings → Webhooks → Add webhook
2. Payload URL: `https://cf-article-checker.<your-subdomain>.workers.dev/webhook`
3. Content type: `application/json`
4. Events: Select "Issue comments" only
5. Secret: `WEBHOOK_SECRET` (**required** — used to verify `X-Hub-Signature-256` HMAC. Worker rejects all unsigned requests.)

## Testing

```bash
npm test
```

### 🌰 Test Coverage

- Webhook event filtering (non-comment events, non-created actions, missing `/articlecheck`)
- Permission checks (authorized vs unauthorized reviewers, case-insensitive matching)
- Request validation (invalid JSON handling)
- Trigger verification (valid requests, `/articlecheck` with surrounding text)
- PR detection (regular issues vs pull requests)

## Usage

Comment `/articlecheck` on any pull request to trigger the automated review. Only users listed in the `REVIEWERS` secret can trigger the check.

## File Structure

```text
cf-article-checker/
├── src/
│   └── index.ts          # Main worker: webhook handler + Claude/Search pipeline
├── test/
│   ├── index.spec.ts     # Integration tests
│   └── tsconfig.json     # Test TypeScript config
├── package.json
├── tsconfig.json
├── vitest.config.ts
└── wrangler.toml
```

## 🌰🌰🌰
