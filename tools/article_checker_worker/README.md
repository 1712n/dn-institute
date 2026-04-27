# dn-article-checker (Cloudflare Workers)

Webhook-based migration of the article-check QA bot. Replaces the GitHub Actions
workflow at `.github/workflows/article-check-claude.yml`.

## How it works

1. GitHub posts an `issue_comment` webhook to this Worker when someone comments
   on a PR.
2. Worker verifies the HMAC-SHA256 signature, filters to `/articlecheck` from a
   reviewer in `WIKI_REVIEWERS`, fetches the PR diff, runs the article checks
   (fact-check + editor notes + format check), posts the report as a PR comment.
3. The Worker uses `ctx.waitUntil()` to handle the LLM calls async, so the
   webhook returns 202 to GitHub within seconds.

## Local development

```bash
cd tools/article_checker_worker
npm install
wrangler dev
```

## Secrets / config

Set via `wrangler secret put`:
- `GITHUB_APP_TOKEN` -- GitHub PAT with `pull_request:write` and `issues:write`
- `WEBHOOK_SECRET` -- shared secret used for HMAC signature
- `ANTHROPIC_API_KEY`
- `BRAVE_API_KEY`

Set via `[vars]` in `wrangler.toml` or dashboard:
- `WIKI_REVIEWERS` -- JSON array of allowed GitHub logins

## Status

**DRAFT.** Worker scaffold + signature + permission check + PR fetch + comment
post are wired. The LLM check logic (port of `article_checker_claude.py`) is
stubbed pending maintainer review of the design questions in the PR description.
