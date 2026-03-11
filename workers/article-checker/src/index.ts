// 🌰 Article Checker — Cloudflare Worker 🌰
//
// Webhook-based serverless replacement for the GitHub Actions article-check-claude bot.
// Receives GitHub issue_comment webhooks, verifies the /articlecheck command,
// then runs fact-checking and quality review on the PR's article content.
//
// 🌰 Architecture:
// - Accepts webhook → verifies signature → returns 200 immediately
// - Uses waitUntil() to process the article check asynchronously
// - Posts results as a PR comment when done

import { Hono } from "hono";
import type { Env, IssueCommentPayload } from "./types";
import { verifyWebhookSignature } from "./crypto";
import { parseDiff, extractArticleText } from "./diff-parser";
import {
  getPullRequestDiff,
  createPRComment,
  addCommentReaction,
} from "./github";
import { runArticleCheck } from "./claude";

type HonoEnv = { Bindings: Env };

const app = new Hono<HonoEnv>();

// 🌰 Health check endpoint
app.get("/", (c) => c.text("🌰 Article Checker Worker is running 🌰"));

// 🌰 Main webhook endpoint
app.post("/webhook", async (c) => {
  const env = c.env;

  // 🌰 Read the raw body for signature verification
  const rawBody = await c.req.text();
  const signature = c.req.header("x-hub-signature-256") ?? "";

  // 🌰 Verify webhook signature
  const isValid = await verifyWebhookSignature(
    rawBody,
    signature,
    env.GITHUB_WEBHOOK_SECRET,
  );
  if (!isValid) {
    console.error("🌰 Invalid webhook signature");
    return c.text("Invalid signature", 401);
  }

  // 🌰 Parse the payload
  let payload: IssueCommentPayload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return c.text("Invalid JSON", 400);
  }

  // 🌰 Only process newly created comments
  if (payload.action !== "created") {
    return c.text("Ignored: not a created comment", 200);
  }

  // 🌰 Only process comments on PRs (not plain issues)
  if (!payload.issue.pull_request) {
    return c.text("Ignored: not a PR comment", 200);
  }

  // 🌰 Check for the /articlecheck command
  if (!payload.comment.body.includes("/articlecheck")) {
    return c.text("Ignored: no /articlecheck command", 200);
  }

  // 🌰 Permission check: is the commenter an authorized reviewer?
  let reviewers: string[];
  try {
    reviewers = JSON.parse(env.WIKI_REVIEWERS);
  } catch {
    console.error("🌰 Failed to parse WIKI_REVIEWERS");
    return c.text("Server configuration error", 500);
  }

  const actor = payload.comment.user.login;
  if (!reviewers.includes(actor)) {
    console.log(`🌰 Unauthorized user: ${actor}`);
    return c.text("Unauthorized", 403);
  }

  // 🌰 All checks passed — acknowledge and process asynchronously
  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;
  const prNumber = payload.issue.number;
  const commentId = (payload.comment as { id?: number }).id;

  // 🌰 Use waitUntil() to process without blocking the webhook response
  c.executionCtx.waitUntil(
    processArticleCheck(env, owner, repo, prNumber, commentId),
  );

  return c.text("🌰 Processing started", 202);
});

/**
 * 🌰 Async article check pipeline.
 * Runs after the webhook response has been sent.
 */
async function processArticleCheck(
  env: Env,
  owner: string,
  repo: string,
  prNumber: number,
  commentId?: number,
): Promise<void> {
  try {
    // 🌰 React to the trigger comment with 👀 to signal processing
    if (commentId) {
      await addCommentReaction(owner, repo, commentId, "eyes", env.GITHUB_TOKEN);
    }

    // 🌰 Step 1: Fetch the PR diff
    console.log(`🌰 Fetching diff for ${owner}/${repo}#${prNumber}`);
    const diff = await getPullRequestDiff(
      owner,
      repo,
      prNumber,
      env.GITHUB_TOKEN,
    );

    // 🌰 Step 2: Parse the diff and extract article text
    const files = parseDiff(diff);
    const articleText = extractArticleText(files);

    if (!articleText || articleText.trim().length === 0) {
      await createPRComment(
        owner,
        repo,
        prNumber,
        "🌰 **Article Check**: No article content found in this PR's diff.",
        env.GITHUB_TOKEN,
      );
      return;
    }

    // 🌰 Step 3: Run the full article check pipeline
    const review = await runArticleCheck(
      articleText,
      env.ANTHROPIC_API_KEY,
      env.BRAVE_SEARCH_API_KEY,
    );

    // 🌰 Step 4: Post the review as a PR comment
    await createPRComment(owner, repo, prNumber, review, env.GITHUB_TOKEN);
    console.log(`🌰 Article check complete for ${owner}/${repo}#${prNumber}`);
  } catch (error) {
    console.error("🌰 Article check failed:", error);

    // 🌰 Post an error comment so the reviewer knows something went wrong
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    try {
      await createPRComment(
        owner,
        repo,
        prNumber,
        `🌰 **Article Check Failed**\n\nAn error occurred while processing this PR:\n\`\`\`\n${errorMessage}\n\`\`\`\nPlease try again or check the worker logs.`,
        env.GITHUB_TOKEN,
      );
    } catch {
      console.error("🌰 Failed to post error comment");
    }
  }
}

// 🌰 Export the worker fetch handler
export default app;
