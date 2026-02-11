# 🌰 Article Check Worker

Cloudflare Worker that performs automated QA checks on article PRs. Migrated from the GitHub Actions-based `article-check-claude.yml` workflow.

## Architecture 🌰

**Single worker, no external infrastructure.** The worker:

1. Receives GitHub `issue_comment` webhooks
2. Verifies `X-Hub-Signature-256` (HMAC-SHA256)
3. Checks the commenter is in the `WIKI_REVIEWERS` allowlist
4. Returns `202 Accepted` immediately
5. Processes the article asynchronously via `ctx.waitUntil()`:
   - Fetches PR files from GitHub API (parallel fetch for multi-file PRs)
   - Filters to article files (`content/**/*.md`)
   - Runs 3-stage Claude fact-checking pipeline per article
   - Posts results as a PR comment

No Queues, no KV, no Durable Objects. Fetch wait time doesn't count toward the 30-second CPU limit, so the entire pipeline runs within a single worker invocation. 🌰

## Setup

### 1. Install dependencies

```bash
cd workers/articlecheck
npm install
```

### 2. Configure secrets

```bash
wrangler secret put GITHUB_TOKEN          # GitHub PAT with repo scope
wrangler secret put GITHUB_WEBHOOK_SECRET # Webhook secret for signature verification
wrangler secret put ANTHROPIC_API_KEY     # Claude API key
wrangler secret put BRAVE_API_KEY         # Brave Search API key
```

### 3. Set reviewers

Edit `wrangler.toml` and set the `WIKI_REVIEWERS` variable to a comma-separated list of GitHub usernames:

```toml
[vars]
WIKI_REVIEWERS = "user1,user2,user3"
```

### 4. Deploy 🌰

```bash
wrangler deploy
```

### 5. Configure GitHub webhook

In your repo settings → Webhooks → Add webhook:
- **Payload URL**: Your worker URL (shown after `wrangler deploy`)
- **Content type**: `application/json`
- **Secret**: Same value as `GITHUB_WEBHOOK_SECRET`
- **Events**: Select "Issue comments"

## Usage

Authorized reviewers comment `/articlecheck` on a PR to trigger the bot. The worker will:
- Extract factual statements from article files
- Verify each statement via Brave Search + Claude
- Generate an editorial report with fact-check results, editor's notes, Hugo formatting check, and metadata validation
- Post the report as a PR comment 🌰

## Development

```bash
npm run dev    # Start local dev server
npm test       # Run tests
```

## Comparison with Previous Implementation 🌰

| Aspect | GitHub Actions (old) | Cloudflare Worker (new) |
|--------|---------------------|------------------------|
| Trigger | Comment polling via GitHub API | Webhook push (instant) |
| Cold start | ~30s (Poetry install) | <5ms |
| Runtime | Python + Poetry | TypeScript (bundled) |
| Infrastructure | GitHub-hosted runner | Single worker |
| Multi-file | First file only | All article files |
| Search coverage | 1 result per query | 3 results per query |
| Cost | GitHub Actions minutes | Cloudflare Workers free tier 🌰 |
