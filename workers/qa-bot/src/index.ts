/**
 * QA Bot — Cloudflare Worker
 *
 * Migrated from the GitHub Actions workflow (.github/workflows/article-check-claude.yml).
 * Receives GitHub webhook events, verifies signatures, runs the same 3-phase
 * article quality pipeline (extract → fact-check → review), and posts a
 * comment back on the pull request.
 *
 * Supported triggers:
 *   1. Issue comment containing `/articlecheck` (same as legacy bot)
 *   2. pull_request opened / synchronize (automatic checks)
 */

import { Hono } from "hono";
import { verifyWebhookSignature } from "./crypto";
import { fetchPRDiff, parseDiff, postComment } from "./github";
import { runArticleCheck } from "./pipeline";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Env {
  GITHUB_WEBHOOK_SECRET: string;
  GITHUB_TOKEN: string;
  LLM_API_KEY: string;
  SEARCH_API_KEY: string;
  WIKI_REVIEWERS: string; // JSON array string, e.g. '["user1","user2"]'
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

const app = new Hono<{ Bindings: Env }>();

/**
 * Health check endpoint.
 */
app.get("/", (c) => c.text("QA Bot Worker is running"));

/**
 * Main webhook endpoint — receives GitHub events.
 */
app.post("/webhook", async (c) => {
  const body = await c.req.text();
  const signature = c.req.header("x-hub-signature-256") ?? "";

  // 1. Verify webhook signature (HMAC-SHA256)
  const valid = await verifyWebhookSignature(
    body,
    signature,
    c.env.GITHUB_WEBHOOK_SECRET
  );
  if (!valid) {
    return c.text("Invalid signature", 401);
  }

  const event = c.req.header("x-github-event") ?? "";
  const payload = JSON.parse(body);

  // 2. Route by event type
  if (event === "issue_comment") {
    return handleIssueComment(c, payload);
  }
  if (event === "pull_request") {
    return handlePullRequest(c, payload);
  }

  return c.text("Ignored event", 200);
});

// ---------------------------------------------------------------------------
// Event handlers
// ---------------------------------------------------------------------------

async function handleIssueComment(
  c: { env: Env; text: (t: string, s?: number) => Response },
  payload: any
): Promise<Response> {
  // Only react to new comments on pull requests containing /articlecheck
  if (!payload.issue?.pull_request) return c.text("Not a PR comment", 200);
  if (payload.action !== "created") return c.text("Ignored action", 200);

  const commentBody: string = payload.comment?.body ?? "";
  if (!commentBody.includes("/articlecheck")) {
    return c.text("No trigger command", 200);
  }

  // Access control — check if the commenter is an allowed reviewer
  const actor: string = payload.comment?.user?.login ?? "";
  let reviewers: string[] = [];
  try {
    reviewers = JSON.parse(c.env.WIKI_REVIEWERS);
  } catch {
    /* empty or invalid — deny all */
  }
  if (!reviewers.includes(actor)) {
    return c.text("Unauthorized user", 403);
  }

  // Fetch PR details
  const prUrl: string = payload.issue.pull_request.url; // API URL
  const repoFullName: string = payload.repository.full_name;
  const prNumber: number = payload.issue.number;

  return runCheck(c, repoFullName, prNumber, prUrl);
}

async function handlePullRequest(
  c: { env: Env; text: (t: string, s?: number) => Response },
  payload: any
): Promise<Response> {
  const action: string = payload.action ?? "";
  if (action !== "opened" && action !== "synchronize") {
    return c.text("Ignored PR action", 200);
  }

  const repoFullName: string = payload.repository.full_name;
  const prNumber: number = payload.pull_request.number;
  const prApiUrl: string = payload.pull_request.url;

  return runCheck(c, repoFullName, prNumber, prApiUrl);
}

// ---------------------------------------------------------------------------
// Core orchestration
// ---------------------------------------------------------------------------

async function runCheck(
  c: { env: Env; text: (t: string, s?: number) => Response },
  repoFullName: string,
  prNumber: number,
  prApiUrl: string
): Promise<Response> {
  try {
    // 1. Fetch & parse the PR diff
    const rawDiff = await fetchPRDiff(prApiUrl, c.env.GITHUB_TOKEN);
    const files = parseDiff(rawDiff);

    if (files.length === 0) {
      return c.text("No article files in diff", 200);
    }

    // 2. Run the 3-phase pipeline on each article file
    const results: string[] = [];
    for (const file of files) {
      const review = await runArticleCheck(
        file.filename,
        file.content,
        c.env.LLM_API_KEY,
        c.env.SEARCH_API_KEY
      );
      results.push(review);
    }

    // 3. Post comment(s) on the PR
    const comment = results.join("\n\n---\n\n");
    await postComment(repoFullName, prNumber, comment, c.env.GITHUB_TOKEN);

    return c.text("Check complete", 200);
  } catch (err: any) {
    console.error("runCheck error:", err);
    return c.text(`Error: ${err.message}`, 500);
  }
}

export default app;
