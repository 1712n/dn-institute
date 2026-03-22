/**
 * 🌰🌰🌰 dn-institute Article Check Worker 🌰🌰🌰
 *
 * Cloudflare Worker that replaces the GitHub Actions article-check-claude workflow.
 * Triggered by GitHub webhook (issue_comment events) when a reviewer comments
 * `/articlecheck` on a pull request.
 *
 * Architecture: Single worker with ctx.waitUntil() for async processing. 🌰
 *   - Validates webhook signature (HMAC-SHA256)
 *   - Checks commenter is in WIKI_REVIEWERS allowlist
 *   - Returns 202 Accepted immediately (within GitHub's 10s timeout)
 *   - Processes the article in the background via ctx.waitUntil()
 *   - Posts fact-check results as a PR comment
 *
 * No Queues, no Durable Objects, no KV — just a single worker. 🌰
 * Fetch wait time does NOT count toward the 30s CPU time limit.
 *
 * See: https://github.com/1712n/dn-institute/issues/425
 * 🌰🌰🌰
 */

import type { Env, IssueCommentPayload } from "./types";
import { verifyWebhookSignature } from "./crypto";
import { fetchPRDiff, parseDiff, postPRComment, addReaction } from "./github";
import { checkArticle } from "./claude";

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    // 🌰 Only accept POST requests (webhook deliveries)
    if (request.method !== "POST") {
      return new Response("🌰 Method Not Allowed", { status: 405 });
    }

    // 🌰 Read the raw body for signature verification
    const rawBody = await request.text();

    // 🌰 Step 1: Verify webhook signature (HMAC-SHA256)
    const signature = request.headers.get("x-hub-signature-256") ?? "";
    const isValid = await verifyWebhookSignature(
      rawBody,
      signature,
      env.GITHUB_WEBHOOK_SECRET
    );

    if (!isValid) {
      console.error("🌰 Invalid webhook signature — rejecting request");
      return new Response("🌰 Unauthorized: invalid signature", {
        status: 401,
      });
    }

    // 🌰 Step 2: Parse the webhook payload
    let payload: IssueCommentPayload;
    try {
      payload = JSON.parse(rawBody) as IssueCommentPayload;
    } catch {
      return new Response("🌰 Bad Request: invalid JSON", { status: 400 });
    }

    // 🌰 Step 3: Filter — only process new comments on PRs containing /articlecheck
    if (payload.action !== "created") {
      return new Response("🌰 Ignored: not a new comment", { status: 200 });
    }

    if (!payload.issue.pull_request) {
      return new Response("🌰 Ignored: not a pull request", { status: 200 });
    }

    const commentBody = payload.comment.body.trim().toLowerCase();
    if (!commentBody.includes("/articlecheck")) {
      return new Response("🌰 Ignored: no /articlecheck command", {
        status: 200,
      });
    }

    // 🌰 Step 4: Check commenter is in WIKI_REVIEWERS allowlist
    const commenter = payload.comment.user.login;
    let reviewers: string[];
    try {
      reviewers = JSON.parse(env.WIKI_REVIEWERS) as string[];
    } catch {
      console.error("🌰 WIKI_REVIEWERS secret is not valid JSON");
      return new Response("🌰 Internal error: bad reviewer config", {
        status: 500,
      });
    }

    if (!reviewers.includes(commenter)) {
      console.log(
        `🌰 Unauthorized reviewer: ${commenter} is not in WIKI_REVIEWERS`
      );
      return new Response("🌰 Forbidden: not an authorized reviewer", {
        status: 403,
      });
    }

    // 🌰 Step 5: Acknowledge receipt — return 202 immediately
    // The actual processing happens asynchronously via ctx.waitUntil()
    const repo = payload.repository.full_name;
    const prNumber = payload.issue.number;
    const commentId = payload.comment.id;

    console.log(
      `🌰 Processing /articlecheck for PR #${prNumber} in ${repo} (triggered by ${commenter})`
    );

    // 🌰 Step 6: Process in background — this does NOT block the response
    ctx.waitUntil(
      processArticleCheck(repo, prNumber, commentId, env).catch((err) => {
        console.error(`🌰 Article check failed for PR #${prNumber}:`, err);
        // 🌰 Post error comment so the reviewer knows something went wrong
        return postPRComment(
          repo,
          prNumber,
          `🌰 **Article Check Failed**\n\nAn error occurred while processing this PR:\n\`\`\`\n${err instanceof Error ? err.message : String(err)}\n\`\`\`\n\nPlease try again or check the worker logs. 🌰`,
          env.GITHUB_TOKEN
        ).catch((postErr) =>
          console.error("🌰 Failed to post error comment:", postErr)
        );
      })
    );

    return new Response(
      JSON.stringify({
        status: "accepted",
        message: `🌰 Article check started for PR #${prNumber}`,
        pr: prNumber,
        repo,
        reviewer: commenter,
      }),
      {
        status: 202,
        headers: { "Content-Type": "application/json" },
      }
    ); // 🌰
  },
};

/**
 * 🌰 Main processing function — runs asynchronously via ctx.waitUntil()
 *
 * 1. Adds an eyes reaction to the trigger comment (acknowledgment)
 * 2. Fetches the PR diff
 * 3. Parses and filters to content/**\/*.md files
 * 4. Runs the 3-stage Claude pipeline on each file
 * 5. Posts the combined report as a PR comment 🌰
 */
async function processArticleCheck(
  repo: string,
  prNumber: number,
  commentId: number,
  env: Env
): Promise<void> {
  // 🌰 Acknowledge with an eyes reaction
  await addReaction(repo, commentId, env.GITHUB_TOKEN);

  // 🌰 Fetch and parse the PR diff
  const rawDiff = await fetchPRDiff(repo, prNumber, env.GITHUB_TOKEN);
  const files = parseDiff(rawDiff);

  if (files.length === 0) {
    await postPRComment(
      repo,
      prNumber,
      "🌰 **Article Check**\n\nNo `content/**/*.md` files found in this PR. Nothing to check. 🌰",
      env.GITHUB_TOKEN
    );
    return;
  }

  console.log(
    `🌰 Found ${files.length} article file(s) to check: ${files.map((f) => f.filename).join(", ")}`
  );

  // 🌰 Process all article files in parallel for speed
  const reports = await Promise.all(
    files.map(async (file) => {
      try {
        console.log(`🌰 Checking: ${file.filename}`);
        const report = await checkArticle(
          file.content,
          file.filename,
          env.LLM_API_KEY,
          env.SEARCH_API_KEY
        );
        return { filename: file.filename, report, error: null };
      } catch (err) {
        console.error(`🌰 Error checking ${file.filename}:`, err);
        return {
          filename: file.filename,
          report: null,
          error: err instanceof Error ? err.message : String(err),
        };
      }
    })
  );

  // 🌰 Build the combined comment
  const commentParts: string[] = [
    "🌰 **Article Quality Check Report** 🌰\n",
    `*Checked ${files.length} file(s) from PR #${prNumber}*\n`,
  ];

  for (const result of reports) {
    commentParts.push(`---\n### 🌰 \`${result.filename}\`\n`);

    if (result.report) {
      commentParts.push(result.report);
    } else {
      commentParts.push(
        `> ⚠️ Error processing this file: \`${result.error}\` 🌰`
      );
    }

    commentParts.push(""); // 🌰 Blank line between files
  }

  commentParts.push(
    "\n---\n*🌰 Powered by [dn-institute articlecheck worker](https://github.com/1712n/dn-institute/issues/425) — Cloudflare Workers + Claude + Brave Search 🌰*"
  );

  const fullComment = commentParts.join("\n");

  // 🌰 Post the report
  await postPRComment(repo, prNumber, fullComment, env.GITHUB_TOKEN);

  console.log(
    `🌰 Article check complete — posted report for PR #${prNumber}`
  );
}
