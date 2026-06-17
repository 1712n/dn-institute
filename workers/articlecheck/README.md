# Cloudflare Workers Article Check Bot (Issue #425)

This folder contains a webhook-based replacement for the GitHub Actions QA bot (`/articlecheck`), implemented as **two Cloudflare Workers** connected by a **Cloudflare Queue**:

- **Producer worker** (`producer/`): receives GitHub `issue_comment` webhooks, verifies signature, checks reviewer allowlist, enqueues a job, and responds quickly (GitHub webhook timeout friendly).
- **Consumer worker** (`consumer/`): consumes queued jobs, fetches PR article content, runs the Claude + Brave fact-check pipeline, and posts a comment back on the PR.

Idempotency is enforced via:
- KV keys for `delivery_id` and `comment_id`
- a hidden HTML marker embedded in the posted PR comment

## Prereqs

- Cloudflare account with Workers, Queues, and KV enabled.
- A GitHub App installed on the target repo (recommended for least-privilege auth).
- Anthropic API key (Claude).
- Brave Search API key.

## GitHub App Setup (Recommended)

1. Create a GitHub App (Organization or personal, depending on where the repo lives).
2. Enable **webhooks** and set:
   - Webhook URL: your deployed Producer worker URL (for example `https://dn-institute-articlecheck-producer.<your-subdomain>.workers.dev/`)
   - Webhook secret: generate one and store it as `GITHUB_WEBHOOK_SECRET` in the Producer worker.
3. Subscribe to events:
   - **Issue comments**
4. Permissions (minimum):
   - Repository permissions:
     - Contents: Read
     - Pull requests: Read
     - Issues: Read + Write (to post comments on PRs; PRs are issues in GitHub API)
5. Install the GitHub App on the repo.
6. Download the App private key (`.pem`) and store it as a secret for the Consumer worker (`GITHUB_APP_PRIVATE_KEY`).

The webhook payload includes `installation.id`, which the Consumer uses to mint an installation token.

## Cloudflare Setup

### 1) Create Queue

Create a queue named `dn-institute-articlecheck`:

```bash
wrangler queues create dn-institute-articlecheck
```

### 2) Create KV Namespace

Create a KV namespace for idempotency:

```bash
wrangler kv namespace create ARTICLECHECK_DEDUP
```

Update `consumer/wrangler.toml` with the returned KV namespace id.

## Configure Secrets / Vars

### Producer (`producer/`)

Secrets:

```bash
wrangler secret put GITHUB_WEBHOOK_SECRET
```

Vars:
- `WIKI_REVIEWERS`: JSON array of allowed GitHub usernames (preferred), matching the existing GitHub Actions behavior.
  - Example: `["harmatta","someReviewer"]`

### Consumer (`consumer/`)

Secrets:

```bash
wrangler secret put GITHUB_APP_PRIVATE_KEY
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put BRAVE_API_KEY
```

Vars:
- `GITHUB_APP_ID`: numeric GitHub App id
- Optional tuning:
  - `ANTHROPIC_MODEL` (default: `claude-3-opus-20240229`)
  - `ANTHROPIC_TEMPERATURE` (default: `0`)
  - `MAX_STATEMENTS` (default: `12`)
  - `MAX_SEARCH_RESULTS` (default: `3`)
  - `MAX_FILES` (default: `1`)
  - `MAX_ARTICLE_CHARS` (default: `60000`)
  - `DEDUP_TTL_SECONDS` (default: `604800` = 7 days)

## Deploy

From this folder:

```bash
# Producer
wrangler deploy --config producer/wrangler.toml

# Consumer
wrangler deploy --config consumer/wrangler.toml
```

## Behavior Notes

- Trigger: new `issue_comment` containing `/articlecheck` on a PR.
- Allowlist gate: the Producer checks `sender.login` is in `WIKI_REVIEWERS` before enqueueing.
- Content fetch strategy (upgrade over diff-only): the Consumer fetches full `content/attacks/*.md` file content at the PR head SHA.
- One comment per run: the Consumer posts a single PR comment containing results (and a hidden marker).

## Local Development / Tests

Typecheck + unit tests live in this folder:

```bash
npm install
npm run typecheck
npm test
```

