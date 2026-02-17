/**
 * Cloudflare Worker entry point for the DN Institute Article Checker bot.
 *
 * This worker replaces the GitHub Actions-based article-check-claude workflow.
 * It listens for GitHub webhook events (issue_comment) and, when a reviewer
 * posts "/articlecheck" on a pull request, fetches the PR diff, runs the
 * article through Claude's fact-checking and editorial pipeline, and posts
 * the results as a PR comment.
 *
 * Webhook setup:
 *   - URL: https://<worker-name>.<account>.workers.dev/webhook
 *   - Content type: application/json
 *   - Events: Issue comments
 *   - Secret: configured via GITHUB_WEBHOOK_SECRET
 */

import type { Env, IssueCommentPayload } from "./types";
import { verifyWebhookSignature } from "./crypto";
import {
  fetchPRDiff,
  parseDiff,
  removePlus,
  postPRComment,
  addCommentReaction,
} from "./github";
import { checkArticle } from "./claude";

const COMMAND_TRIGGER = "/articlecheck";

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === "/" || url.pathname === "/health") {
      return new Response(
        JSON.stringify({
          status: "ok",
          service: "dn-institute-article-checker",
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Webhook endpoint
    if (url.pathname === "/webhook" && request.method === "POST") {
      return handleWebhook(request, env, ctx);
    }

    return new Response("Not Found", { status: 404 });
  },
};

/**
 * Handle incoming GitHub webhook requests.
 * Validates the signature, checks event type, and dispatches processing.
 */
async function handleWebhook(
  request: Request,
  env: Env,
  ctx: ExecutionContext
): Promise<Response> {
  // 1. Verify content type
  const contentType = request.headers.get("Content-Type") || "";
  if (!contentType.includes("application/json")) {
    return new Response("Unsupported content type", { status: 415 });
  }

  // 2. Read the raw body for signature verification
  const rawBody = await request.text();

  // 3. Verify webhook signature
  const signature = request.headers.get("X-Hub-Signature-256") || "";
  const isValid = await verifyWebhookSignature(
    rawBody,
    signature,
    env.GITHUB_WEBHOOK_SECRET
  );

  if (!isValid) {
    console.error("Webhook signature verification failed");
    return new Response("Unauthorized", { status: 401 });
  }

  // 4. Check event type
  const event = request.headers.get("X-GitHub-Event");
  if (event !== "issue_comment") {
    // We only handle issue_comment events; acknowledge others silently
    return new Response(
      JSON.stringify({ message: `Event '${event}' ignored` }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // 5. Parse the payload
  let payload: IssueCommentPayload;
  try {
    payload = JSON.parse(rawBody) as IssueCommentPayload;
  } catch {
    return new Response("Invalid JSON payload", { status: 400 });
  }

  // 6. Check if this is a relevant event
  if (!shouldProcess(payload, env)) {
    return new Response(
      JSON.stringify({ message: "Event not relevant, skipping" }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  // 7. Process the article check asynchronously using waitUntil
  //    This allows us to respond to GitHub quickly (within 10s) while
  //    the actual processing continues in the background.
  ctx.waitUntil(processArticleCheck(payload, env));

  return new Response(
    JSON.stringify({ message: "Article check initiated" }),
    {
      status: 202,
      headers: { "Content-Type": "application/json" },
    }
  );
}

/**
 * Determine whether a webhook payload should trigger processing.
 * Checks:
 *   - The comment was just created (not edited/deleted)
 *   - The comment is on a pull request
 *   - The comment body contains the /articlecheck command
 *   - The commenter is in the allowed reviewers list
 */
function shouldProcess(payload: IssueCommentPayload, env: Env): boolean {
  // Only process newly created comments
  if (payload.action !== "created") {
    console.log(`Ignoring comment action: ${payload.action}`);
    return false;
  }

  // Must be on a pull request
  if (!payload.issue.pull_request) {
    console.log("Comment is not on a pull request, ignoring");
    return false;
  }

  // Must contain the trigger command
  if (!payload.comment.body.includes(COMMAND_TRIGGER)) {
    console.log("Comment does not contain /articlecheck command, ignoring");
    return false;
  }

  // Commenter must be in the allowed reviewers list
  const commenter = payload.comment.body ? payload.comment.user.login : "";
  let reviewers: string[] = [];
  try {
    reviewers = JSON.parse(env.WIKI_REVIEWERS);
  } catch {
    console.error("Failed to parse WIKI_REVIEWERS secret");
    return false;
  }

  if (!reviewers.includes(commenter)) {
    console.log(
      `User '${commenter}' is not in the allowed reviewers list, ignoring`
    );
    return false;
  }

  return true;
}

/**
 * Main processing function that runs the full article check pipeline.
 * This is executed via ctx.waitUntil() so it runs in the background
 * after the webhook response has been sent.
 */
async function processArticleCheck(
  payload: IssueCommentPayload,
  env: Env
): Promise<void> {
  const repo = payload.repository.full_name;
  const prNumber = payload.issue.number;
  const commentId =
    payload.comment && "id" in payload.comment
      ? (payload.comment as unknown as { id: number }).id
      : 0;

  console.log(`Processing article check for ${repo}#${prNumber}`);

  try {
    // Acknowledge receipt with an "eyes" reaction
    if (commentId) {
      await addCommentReaction(repo, commentId, "eyes", env.GITHUB_TOKEN);
    }

    // 1. Fetch the PR diff
    console.log("Fetching PR diff...");
    const rawDiff = await fetchPRDiff(repo, prNumber, env.GITHUB_TOKEN);

    // 2. Parse the diff
    const files = parseDiff(rawDiff);
    if (files.length === 0) {
      await postPRComment(
        repo,
        prNumber,
        "No file changes found in this pull request.",
        env.GITHUB_TOKEN
      );
      return;
    }

    // 3. Extract the article text from the first file's diff
    //    (mirrors the Python: text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body']))
    const firstFile = files[0];
    let articleText = firstFile.header;
    if (firstFile.body.length > 0) {
      articleText += firstFile.body[0].body;
    }
    articleText = removePlus(articleText);

    if (!articleText.trim()) {
      await postPRComment(
        repo,
        prNumber,
        "Could not extract article text from the pull request diff.",
        env.GITHUB_TOKEN
      );
      return;
    }

    console.log(`Extracted article text (${articleText.length} chars)`);

    // 4. Run the article check pipeline
    const result = await checkArticle(articleText, env);

    // 5. Post the result as a PR comment
    const comment = `## Article Check Results\n\n${result}`;
    await postPRComment(repo, prNumber, comment, env.GITHUB_TOKEN);

    // Add a rocket reaction to indicate success
    if (commentId) {
      await addCommentReaction(repo, commentId, "rocket", env.GITHUB_TOKEN);
    }

    console.log(`Article check completed for ${repo}#${prNumber}`);
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : String(error);
    console.error(`Article check failed for ${repo}#${prNumber}: ${errorMessage}`);

    // Post error notification to the PR
    try {
      await postPRComment(
        repo,
        prNumber,
        `## Article Check Error\n\nThe article check encountered an error:\n\`\`\`\n${errorMessage}\n\`\`\`\nPlease try again or contact the maintainers.`,
        env.GITHUB_TOKEN
      );
    } catch (commentError) {
      console.error("Failed to post error comment:", commentError);
    }
  }
}
