# DN Article Checker — Cloudflare Worker

A serverless replacement for the Python GitHub Actions workflow that QA-checks
articles submitted to the DN Institute repository.

## What it does

When an authorised reviewer posts `/articlecheck` as a comment on a pull
request, the Worker:

1. **Verifies** the GitHub webhook signature (HMAC-SHA256).
2. **Fetches** the PR diff via the GitHub API.
3. **Extracts** factual statements from the article using Claude (`claude-3-opus`).
4. **Fact-checks** each statement with an iterative Brave Search + Claude loop
   (the `</search_query>` stop-sequence pattern).
5. **Generates** an editor's report: fact-check results, editor's notes,
   Hugo SSG formatting check, filename check, metadata headers check.
6. **Posts** the report as a PR comment.

---

## Architecture

```
POST /webhook
    │
    ├─ verifySignature()      — HMAC-SHA256 guard
    ├─ isAuthorised()         — check WIKI_REVIEWERS list
    │
    ├─ 200 OK  ◄──────────── immediate response to GitHub
    │
    └─ ctx.waitUntil(runFactCheck())
            │
            ├─ getPrDiff()          — fetch raw diff via GitHub API
            ├─ parseDiff()          — split into file/hunk segments
            ├─ extractArticleText() — strip '+' diff markers
            │
            └─ fullCheck()
                    ├─ extractStatements()  — Claude extracts factual claims
                    ├─ retrieve()           — iterative search loop
                    │       └─ BraveSearchTool.searchFormatted()
                    └─ answerWithResults()  — Claude generates final report
```

---

## Setup

### 1. Install dependencies

```bash
cd workers/article-checker
npm install
```

### 2. Configure secrets

Set these via `wrangler secret put <KEY>`:

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | GitHub token with `pull-requests: write` permission |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `BRAVE_API_KEY` | Brave Search API key |
| `WEBHOOK_SECRET` | The secret configured on the GitHub webhook |
| `WIKI_REVIEWERS` | Comma-separated GitHub usernames, e.g. `alice,bob,carol` |

```bash
wrangler secret put GITHUB_TOKEN
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put BRAVE_API_KEY
wrangler secret put WEBHOOK_SECRET
wrangler secret put WIKI_REVIEWERS
```

### 3. (Optional) Tune model vars

The `[vars]` block in `wrangler.toml` has sensible defaults. Override any of
them without touching secrets:

| Var | Default | Description |
|-----|---------|-------------|
| `ANTHROPIC_SEARCH_MODEL` | `claude-3-opus-20240229` | Model for fact-checking |
| `ANTHROPIC_SUMMARIZE_MODEL` | `claude-3-haiku-20240307` | Lighter model (reserved) |
| `ANTHROPIC_SEARCH_MAX_TOKENS` | `4000` | Max tokens per retrieval call |
| `ANTHROPIC_ANSWER_MAX_TOKENS` | `4096` | Max tokens for the final report |
| `N_SEARCH_RESULTS` | `3` | Brave results per search query |
| `MAX_SEARCHES` | `5` | Max search iterations per article |

### 4. Deploy

```bash
wrangler deploy
```

Note the Worker URL that Wrangler prints — you'll need it in step 5.

### 5. Configure the GitHub webhook

In the DN Institute repo → **Settings → Webhooks → Add webhook**:

| Field | Value |
|-------|-------|
| Payload URL | `https://dn-article-checker.<your-account>.workers.dev/webhook` |
| Content type | `application/json` |
| Secret | *(same value you used for `WEBHOOK_SECRET`)* |
| Which events? | Let me select → **Issue comments** |

---

## Local development

```bash
wrangler dev
```

To test the webhook locally, use the [Wrangler tunnel](https://developers.cloudflare.com/workers/wrangler/commands/#dev)
or a tool like `ngrok` to expose your local port, then point the GitHub webhook
at the tunnel URL.

---

## Differences from the Python implementation

| Aspect | Python (GitHub Actions) | This Worker |
|--------|------------------------|-------------|
| Trigger | Workflow polling issue_comment events | Push webhook — instant |
| Web-page scraping | aiohttp + BeautifulSoup | Not done — uses Brave description snippets (avoids scraping in serverless) |
| Response time | 2–5 min (cold start + install) | Immediate 200; async in `ctx.waitUntil` |
| Cost | GitHub Actions minutes | Cloudflare Workers (free tier covers most usage) |
| Model config | Hardcoded in `config.json` | Configurable via `wrangler.toml` vars |

---

## File structure

```
workers/article-checker/
├── README.md
├── package.json
├── tsconfig.json
├── wrangler.toml
└── src/
    ├── index.ts      ← Hono app, Worker entry point
    ├── webhook.ts    ← Signature verification, event parsing, authorisation
    ├── github.ts     ← GitHub API: diff fetch, parse, post comment
    ├── prompts.ts    ← Claude prompts (exact ports from Python)
    ├── search.ts     ← Brave Search integration + result formatting
    └── checker.ts    ← Fact-checking pipeline (extract → retrieve → answer)
```
