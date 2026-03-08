import { Hono } from "hono";
import type { Env, IssueCommentPayload, PullRequestPayload } from "./types";
import {
  verifyGitHubWebhook,
  fetchDiff,
  parseDiff,
  postComment,
  getPrDiffUrl,
} from "./github";
import { analyzeArticle } from "./analyzer";

const app = new Hono<{ Bindings: Env }>();

/** Health check */
app.get("/", (c) => c.text("QA Bot Worker is running"));

/**
 * GitHub webhook endpoint.
 *
 * Supports two trigger modes:
 *   1. issue_comment — triggered by `/articlecheck` command in a PR comment
 *   2. pull_request  — triggered by PR opened / synchronize events
 */
app.post("/webhook", async (c) => {
  const rawBody = await c.req.text();

  // 1. Verify webhook signature
  const signature = c.req.header("X-Hub-Signature-256") ?? null;
  const isValid = await verifyGitHubWebhook(
    rawBody,
    signature,
    c.env.GITHUB_WEBHOOK_SECRET
  );

  if (!isValid) {
    return c.text("Invalid signature", 401);
  }

  const event = c.req.header("X-GitHub-Event");
  const payload = JSON.parse(rawBody);

  // 2. Route by event type
  if (event === "issue_comment") {
    return handleIssueComment(c, payload as IssueCommentPayload);
  }

  if (event === "pull_request") {
    return handlePullRequest(c, payload as PullRequestPayload);
  }

  return c.text("Event ignored", 200);
});

/**
 * Handle issue_comment events:
 * Only process if the comment is on a PR and contains `/articlecheck`.
 */
async function handleIssueComment(
  c: { env: Env; text: (body: string, status?: number) => Response },
  payload: IssueCommentPayload
): Promise<Response> {
  // Must be a newly created comment
  if (payload.action !== "created") {
    return c.text("Not a new comment", 200);
  }

  // Must contain the trigger command
  if (!payload.comment.body.includes("/articlecheck")) {
    return c.text("No /articlecheck command", 200);
  }

  // Must be on a pull request
  if (!payload.issue.pull_request) {
    return c.text("Not a pull request comment", 200);
  }

  try {
    const prInfo = await getPrDiffUrl(
      payload.issue.pull_request.url,
      c.env.GITHUB_TOKEN
    );

    const diff = await fetchDiff(prInfo.diffUrl, c.env.GITHUB_TOKEN);
    const files = parseDiff(diff);

    const result = await analyzeArticle(
      files,
      c.env.ANTHROPIC_API_KEY,
      c.env.BRAVE_API_KEY,
      c.env.ANTHROPIC_MODEL,
      parseInt(c.env.ANTHROPIC_MAX_TOKENS, 10)
    );

    await postComment(
      payload.repository.full_name,
      payload.issue.number,
      `## 🤖 QA Bot Review\n\n${result}`,
      c.env.GITHUB_TOKEN
    );

    return c.text("Review posted", 200);
  } catch (err) {
    console.error("Error in issue_comment handler:", err);
    return c.text(`Error: ${(err as Error).message}`, 500);
  }
}

/**
 * Handle pull_request events:
 * Auto-trigger on opened or synchronize actions.
 */
async function handlePullRequest(
  c: { env: Env; text: (body: string, status?: number) => Response },
  payload: PullRequestPayload
): Promise<Response> {
  if (payload.action !== "opened" && payload.action !== "synchronize") {
    return c.text("PR action ignored", 200);
  }

  try {
    const diff = await fetchDiff(
      payload.pull_request.diff_url,
      c.env.GITHUB_TOKEN
    );
    const files = parseDiff(diff);

    const result = await analyzeArticle(
      files,
      c.env.ANTHROPIC_API_KEY,
      c.env.BRAVE_API_KEY,
      c.env.ANTHROPIC_MODEL,
      parseInt(c.env.ANTHROPIC_MAX_TOKENS, 10)
    );

    await postComment(
      payload.repository.full_name,
      payload.number,
      `## 🤖 QA Bot Review\n\n${result}`,
      c.env.GITHUB_TOKEN
    );

    return c.text("Review posted", 200);
  } catch (err) {
    console.error("Error in pull_request handler:", err);
    return c.text(`Error: ${(err as Error).message}`, 500);
  }
}

export default app;
