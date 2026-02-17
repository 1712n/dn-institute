# Article Checker - Cloudflare Worker

A Cloudflare Worker that performs automated PR quality checks for the DN Institute Crypto Attack Wiki. This replaces the previous GitHub Actions-based `article-check-claude` workflow.

## How It Works

1. A GitHub webhook sends `issue_comment` events to the worker
2. When an authorized reviewer comments `/articlecheck` on a pull request, the worker:
   - Fetches the PR diff from GitHub
   - Extracts factual statements using Claude
   - Fact-checks each statement using Brave Search + Claude
   - Generates an editorial report with format/metadata checks
   - Posts the results as a PR comment

## Setup

### Prerequisites

- [Cloudflare account](https://dash.cloudflare.com/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/) (`npm i -g wrangler`)
- GitHub repository webhook access
- API keys for Anthropic (Claude) and Brave Search

### 1. Configure Secrets

```bash
cd workers/article-checker
wrangler secret put GITHUB_TOKEN
wrangler secret put GITHUB_WEBHOOK_SECRET
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put BRAVE_API_KEY
wrangler secret put WIKI_REVIEWERS  # JSON array, e.g. ["user1","user2"]
```

### 2. Deploy

```bash
npm install
wrangler deploy
```

### 3. Configure GitHub Webhook

In your GitHub repository settings:

- **Payload URL**: `https://dn-institute-article-checker.<your-subdomain>.workers.dev/webhook`
- **Content type**: `application/json`
- **Secret**: Same value as `GITHUB_WEBHOOK_SECRET`
- **Events**: Select "Issue comments"

### Local Development

```bash
npm install
npm run dev
```

## Architecture

```
src/
  index.ts    - Worker entry point, webhook handler, request routing
  types.ts    - TypeScript type definitions
  crypto.ts   - Webhook signature verification (Web Crypto API)
  github.ts   - GitHub API integration (diff fetching, comment posting)
  search.ts   - Brave Search API integration
  claude.ts   - Anthropic Claude API integration (fact-checking pipeline)
  prompts.ts  - LLM prompt templates
```

## Environment Variables

| Variable | Type | Description |
|----------|------|-------------|
| `GITHUB_TOKEN` | Secret | GitHub PAT with repo access |
| `GITHUB_WEBHOOK_SECRET` | Secret | Webhook signature secret |
| `ANTHROPIC_API_KEY` | Secret | Anthropic API key |
| `BRAVE_API_KEY` | Secret | Brave Search API key |
| `WIKI_REVIEWERS` | Secret | JSON array of allowed GitHub usernames |
| `ANTHROPIC_SEARCH_MODEL` | Var | Claude model for fact-checking |
| `ANTHROPIC_SEARCH_MAX_TOKENS` | Var | Max tokens for fact-checking |
| `ANTHROPIC_SEARCH_TEMPERATURE` | Var | Temperature for fact-checking |
| `ANTHROPIC_SUMMARIZE_MODEL` | Var | Claude model for summarization |
| `ANTHROPIC_SUMMARIZE_MAX_TOKENS` | Var | Max tokens for summarization |
| `ANTHROPIC_SUMMARIZE_TEMPERATURE` | Var | Temperature for summarization |
| `GITHUB_REPO` | Var | Target repository (owner/repo) |
