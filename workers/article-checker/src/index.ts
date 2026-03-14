/**
 * index.ts — Cloudflare Worker entry point.
 *
 * Routes:
 *   GET  /          Health check
 *   POST /webhook   GitHub issue_comment webhook handler
 *
 * Architecture:
 *   The webhook handler responds immediately with 200 OK to satisfy GitHub's
 *   10-second delivery timeout, then uses ctx.waitUntil() to run the full
 *   fact-checking pipeline asynchronously (which can take 1–3 minutes for a
 *   long article with many statements).
 */

import { Hono } from "hono";
import { processWebhook } from "./webhook";
import { getPrDiff, parseDiff, extractArticleText, postComment } from "./github";
import { fullCheck } from "./checker";

// ---------------------------------------------------------------------------
// Env type — wrangler.toml vars + secrets
// ---------------------------------------------------------------------------

export interface Env {
  // Secrets (set via `wrangler secret put`)
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  WEBHOOK_SECRET: string;
  WIKI_REVIEWERS: string;

  // Vars (set in wrangler.toml [vars] block — can be overridden)
  ANTHROPIC_SEARCH_MODEL: string;
  ANTHROPIC_SUMMARIZE_MODEL: string;
  ANTHROPIC_SEARCH_MAX_TOKENS: string;
  ANTHROPIC_ANSWER_MAX_TOKENS: string;
  N_SEARCH_RESULTS: string;
  MAX_SEARCHES: string;
}

// ---------------------------------------------------------------------------
// Hono app
// ---------------------------------------------------------------------------

const app = new Hono<{ Bindings: Env }>();

// ---------------------------------------------------------------------------
// GET / — health check
// ---------------------------------------------------------------------------

app.get("/", (c) => {
  return c.json({
    status: "ok",
    service: "dn-article-checker",
    description: "GitHub webhook handler for DN article QA bot",
  });
});

// ---------------------------------------------------------------------------
// POST /webhook — GitHub webhook handler
// ---------------------------------------------------------------------------

app.post("/webhook", async (c) => {
  const env = c.env;
  const ctx = c.executionCtx;

  // --- 1. Validate & parse the webhook (fast path, runs synchronously) ------
  const { result, bodyText: _bodyText } = await processWebhook(
    c.req.raw,
    env.WEBHOOK_SECRET,
    env.WIKI_REVIEWERS
  );

  if (!result.proceed) {
    // Not an error — just not our event. Log and return 200 so GitHub
    // doesn't retry or flag the delivery as failed.
    console.log(`[webhook] skipped: ${result.reason}`);
    return c.json({ ok: true, skipped: true, reason: result.reason });
  }

  const payload = result.payload!;
  const prApiUrl = payload.issue.pull_request!.url;
  const commentsUrl = payload.issue.comments_url;
  const commenter = payload.comment.user.login;

  console.log(
    `[webhook] /articlecheck from @${commenter} on PR ${prApiUrl}`
  );

  // --- 2. Kick off async processing — respond immediately ------------------

  ctx.waitUntil(
    runFactCheck(prApiUrl, commentsUrl, env).catch(async (err) => {
      // Last-resort error handler: try to post a failure comment on the PR
      console.error("[fact-check] unhandled error:", err);
      const errorMsg = err instanceof Error ? err.message : String(err);
      try {
        await postComment(
          commentsUrl,
          `❌ **Article Checker Error**\n\nThe fact-checking bot encountered an unexpected error:\n\`\`\`\n${errorMsg}\n\`\`\`\n\nPlease check the Worker logs for details.`,
          env.GITHUB_TOKEN
        );
      } catch (commentErr) {
        console.error(
          "[fact-check] also failed to post error comment:",
          commentErr
        );
      }
    })
  );

  // Respond before the async work completes (GitHub expects <10s response)
  return c.json({
    ok: true,
    message: "Article check queued — results will be posted as a PR comment.",
  });
});

// ---------------------------------------------------------------------------
// runFactCheck — the async pipeline
// ---------------------------------------------------------------------------

/**
 * Fetch the PR diff, extract article text, run the full QA pipeline, and post
 * the result as a GitHub PR comment.
 */
async function runFactCheck(
  prApiUrl: string,
  commentsUrl: string,
  env: Env
): Promise<void> {
  // -- a. Post an "in progress" comment so reviewers know the bot is running --
  await postComment(
    commentsUrl,
    "⏳ **Article Checker** is running… this may take a few minutes.",
    env.GITHUB_TOKEN
  );

  // -- b. Fetch and parse the PR diff ----------------------------------------
  console.log(`[fact-check] fetching diff: ${prApiUrl}`);
  const rawDiff = await getPrDiff(prApiUrl, env.GITHUB_TOKEN);
  const files = parseDiff(rawDiff);

  if (files.length === 0) {
    await postComment(
      commentsUrl,
      "⚠️ **Article Checker**: No changed files found in this PR diff.",
      env.GITHUB_TOKEN
    );
    return;
  }

  // Extract the article text from the first file's first hunk
  let articleText: string;
  try {
    articleText = extractArticleText(files);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await postComment(
      commentsUrl,
      `⚠️ **Article Checker**: Could not extract article text from diff.\n\`${msg}\``,
      env.GITHUB_TOKEN
    );
    return;
  }

  console.log(
    `[fact-check] article text extracted (${articleText.length} chars), starting check…`
  );

  // -- c. Run the full fact-checking pipeline ---------------------------------
  let report: string;
  try {
    report = await fullCheck(articleText, {
      ANTHROPIC_API_KEY: env.ANTHROPIC_API_KEY,
      BRAVE_API_KEY: env.BRAVE_API_KEY,
      ANTHROPIC_SEARCH_MODEL: env.ANTHROPIC_SEARCH_MODEL,
      ANTHROPIC_SUMMARIZE_MODEL: env.ANTHROPIC_SUMMARIZE_MODEL,
      ANTHROPIC_SEARCH_MAX_TOKENS: env.ANTHROPIC_SEARCH_MAX_TOKENS,
      ANTHROPIC_ANSWER_MAX_TOKENS: env.ANTHROPIC_ANSWER_MAX_TOKENS,
      N_SEARCH_RESULTS: env.N_SEARCH_RESULTS,
      MAX_SEARCHES: env.MAX_SEARCHES,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await postComment(
      commentsUrl,
      `❌ **Article Checker** failed during fact-checking:\n\`\`\`\n${msg}\n\`\`\``,
      env.GITHUB_TOKEN
    );
    return;
  }

  // -- d. Post the report as a PR comment ------------------------------------
  const commentBody = `## 🔍 Article QA Report\n\n${report}`;
  await postComment(commentsUrl, commentBody, env.GITHUB_TOKEN);
  console.log("[fact-check] report posted successfully");
}

// ---------------------------------------------------------------------------
// Default export (CF Workers fetch handler)
// ---------------------------------------------------------------------------

export default {
  fetch: app.fetch,
} satisfies ExportedHandler<Env>;
