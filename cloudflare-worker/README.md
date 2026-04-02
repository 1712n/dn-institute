# Article Checker Cloudflare Worker 🌰

A webhook-based serverless solution for automated PR quality checks on article submissions to the [Crypto Attack Wiki](https://github.com/1712n/dn-institute).

This worker migrates the existing Python QA bot from GitHub Actions to Cloudflare Workers, providing improved resource efficiency, security, and speed.

Fixes #425

## Features

- **Webhook-based**: Responds to GitHub PR comments with `/articlecheck` command
- **Fact-checking**: Uses Claude AI + Brave Search to verify factual statements
- **Editor review**: Checks style, grammar, and formatting compliance
- **Hugo SSG validation**: Ensures Markdown follows Hugo formatting requirements
- **Metadata validation**: Verifies all required headers are present and correct
- **Filename validation**: Checks file naming convention compliance

## Architecture

```
GitHub PR Comment → Webhook → Cloudflare Worker → QA Checks → PR Comment
```

### QA Checks Performed

1. **Fact-Checking** 🔍
   - Extracts factual statements (numbers, dates, organizations)
   - Searches Brave for verification
   - Reports verified/false/unverified with sources

2. **Editor's Notes** 📝
   - Stylistic improvements
   - Grammar corrections
   - Timeline date format verification

3. **Hugo SSG Formatting Check** 📄
   - Markdown compliance
   - Proper formatting structure

4. **Submission Guidelines Check** ✅
   - Filename format: `YYYY-MM-DD-entity-that-was-hacked.md`
   - Required section headers: Summary, Attackers, Losses, Timeline, Security Failure Causes
   - Metadata headers: date, target-entities, entity-types, attack-types, title, loss
   - Cross-validation of metadata values against content

## Setup

### Prerequisites

- Node.js 18+
- Wrangler CLI (`npm install -g wrangler`)
- Cloudflare account

### Installation

```bash
cd cloudflare-worker
npm install
```

### Configuration

1. Copy the example environment file:
```bash
cp .dev.vars.example .dev.vars
```

2. Set up the following secrets via Wrangler:

```bash
# GitHub Personal Access Token (repo scope)
wrangler secret put GITHUB_TOKEN

# GitHub Webhook Secret (for signature verification)
wrangler secret put GITHUB_WEBHOOK_SECRET

# Anthropic API Key (for Claude)
wrangler secret put ANTHROPIC_API_KEY

# Brave Search API Key
wrangler secret put BRAVE_API_KEY

# JSON array of allowed reviewers
wrangler secret put WIKI_REVIEWERS --json '["username1", "username2"]'
```

### Development

```bash
# Run locally
npm run dev

# Test webhook locally (requires tunnel like ngrok)
ngrok http 8787
```

### Deployment

```bash
# Deploy to Cloudflare
npm run deploy
```

### GitHub Webhook Setup

1. Go to your repository settings → Webhooks
2. Add webhook with URL: `https://your-worker.your-subdomain.workers.dev/webhook`
3. Content type: `application/json`
4. Secret: Same as `GITHUB_WEBHOOK_SECRET`
5. Events: Select "Issue comments"

## API Endpoints

### `GET /`
Health check endpoint.

### `POST /webhook`
GitHub webhook handler. Triggers on issue comments containing `/articlecheck`.

### `POST /check`
Manual trigger endpoint for testing.

```json
{
  "pull_url": "https://api.github.com/repos/owner/repo/pulls/123"
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub PAT with repo scope | Yes |
| `GITHUB_WEBHOOK_SECRET` | Secret for webhook signature verification | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes |
| `BRAVE_API_KEY` | Brave Search API key | Yes |
| `WIKI_REVIEWERS` | JSON array of allowed reviewer usernames | Yes |

## Comparison with Original

| Aspect | GitHub Actions | Cloudflare Worker |
|--------|---------------|-------------------|
| Trigger | Polling/Scheduled | Webhook (instant) |
| Cold Start | ~30s | ~0ms |
| Execution Time | Up to 6 hours | Up to 30s (CPU) |
| Cost per Check | ~$0.05-0.10 | ~$0.001-0.01 |
| Scalability | Limited | Auto-scaling |
| Security | OIDC | HMAC signatures |

## Tech Stack

- **Runtime**: Cloudflare Workers (V8 isolates)
- **Framework**: Hono (lightweight web framework)
- **GitHub API**: Octokit REST.js
- **AI**: Anthropic Claude 3.5 Sonnet
- **Search**: Brave Search API

## License

MIT

## Contributing

Contributions welcome! Please ensure all QA checks pass when submitting articles. 🌰
