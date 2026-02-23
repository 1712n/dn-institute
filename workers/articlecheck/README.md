# Article Check Worker

Cloudflare Worker that provides automated QA for pull requests in the [Crypto Attack Wiki](https://github.com/1712n/dn-institute/tree/main/content/attacks). Migrated from the [GitHub Actions workflow](../../.github/workflows/article-check-claude.yml) to a webhook-based serverless architecture.

## Architecture

Single Cloudflare Worker using `ctx.waitUntil()` for async processing:

```
GitHub Webhook (issue_comment)
  |
  v
Worker receives POST
  |-> Verify X-Hub-Signature-256 (HMAC-SHA256, constant-time comparison)
  |-> Check commenter is in WIKI_REVIEWERS allowlist
  |-> Return 202 Accepted immediately
  |
  v  (async via ctx.waitUntil)
Fetch PR diff from GitHub API
  |-> Parse diff, extract content/**/*.md files
  |
  v
Claude pipeline (per file):
  1. Extract factual statements (Claude Haiku - fast)
  2. Iterative fact-checking with Brave Search (Claude Sonnet)
  3. Generate comprehensive review (Claude Sonnet)
     - Fact-check results
     - Editor's notes
     - Hugo SSG formatting check
     - Metadata and filename validation
  |
  v
Post review comment on PR
```

Fetch wait time (API calls to Claude, Brave, GitHub) does not count toward the 30-second CPU limit, so the full pipeline runs within a single worker invocation without needing Queues or Durable Objects.

## Setup

### 1. Create a GitHub Webhook

In the repository settings, create a webhook:
- **Payload URL**: Your worker URL (e.g., `https://articlecheck.<your-subdomain>.workers.dev`)
- **Content type**: `application/json`
- **Secret**: A strong random string (save for the next step)
- **Events**: Select "Issue comments"

### 2. Configure Secrets

```bash
cd workers/articlecheck
wrangler secret put WEBHOOK_SECRET    # The webhook secret from step 1
wrangler secret put GITHUB_TOKEN      # GitHub PAT with repo scope
wrangler secret put ANTHROPIC_API_KEY # Anthropic API key
wrangler secret put BRAVE_API_KEY     # Brave Search API key
wrangler secret put WIKI_REVIEWERS    # JSON array: '["user1","user2"]'
```

### 3. Deploy

```bash
npm install
npm run deploy
```

## Development

```bash
npm install
npm run dev        # Start local development server
npm test           # Run test suite
npm run typecheck  # Type-check without emitting
```

## Usage

Comment `/articlecheck` on any pull request. The worker will:

1. Verify the commenter is authorized
2. Fetch and parse the PR diff
3. Run the QA pipeline on each `content/**/*.md` file
4. Post results as a PR comment

## How It Works

The pipeline preserves the original three-phase approach from the Python bot:

1. **Statement Extraction** (Claude Haiku): Extracts key factual claims (dates, amounts, entities) from the article.

2. **Iterative Fact-Checking** (Claude Sonnet + Brave Search): For each statement, Claude formulates a search query. The worker runs the search via Brave API and feeds results back. This loop repeats until all statements are verified or the search limit is reached.

3. **Review Generation** (Claude Sonnet): Combines fact-check results with editorial review including grammar/style suggestions, Hugo SSG formatting validation, and metadata header checks against submission guidelines.
