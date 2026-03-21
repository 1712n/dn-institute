import type { Env, WebhookPayload, PipelineJob } from "./types";
import {
  verifySignature,
  isAllowedReviewer,
  fetchPrDiff,
  parseDiff,
  extractArticleText,
  postPrComment,
  hasExistingReview,
} from "./github";
import { runPipeline } from "./pipeline";

const MARKER = "<!-- articlecheck-worker -->";
const ERROR_MARKER = "<!-- articlecheck-worker-error -->";

export default {
  /**
   * HTTP handler — receives GitHub webhooks, validates, enqueues pipeline jobs.
   *
   * Responds within milliseconds so GitHub sees a 202 before its 10s timeout.
   * Actual pipeline work happens in the queue consumer below, which gets
   * 15 minutes of wall clock time (vs 30s for waitUntil).
   */
  async fetch(
    request: Request,
    env: Env,
    _ctx: ExecutionContext
  ): Promise<Response> {
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    const body = await request.text();

    // 1. Verify webhook signature (timing-safe)
    const signature = request.headers.get("X-Hub-Signature-256");
    const valid = await verifySignature(
      body,
      signature,
      env.GITHUB_WEBHOOK_SECRET
    );
    if (!valid) {
      return new Response("Invalid signature", { status: 401 });
    }

    // 2. Parse and validate event type
    const event = request.headers.get("X-GitHub-Event");
    if (event !== "issue_comment") {
      return new Response("Ignored event", { status: 200 });
    }

    let payload: WebhookPayload;
    try {
      payload = JSON.parse(body);
    } catch {
      return new Response("Invalid JSON", { status: 400 });
    }

    if (payload.action !== "created") {
      return new Response("Ignored action", { status: 200 });
    }

    if (!payload.comment.body.includes("/articlecheck")) {
      return new Response("No trigger command", { status: 200 });
    }

    if (!payload.issue.pull_request) {
      return new Response("Not a PR", { status: 200 });
    }

    // 3. Check reviewer permissions
    if (
      !isAllowedReviewer(payload.comment.user.login, env.WIKI_REVIEWERS)
    ) {
      return new Response("Unauthorized reviewer", { status: 403 });
    }

    // 4. Idempotency check via KV
    const deliveryId = request.headers.get("X-GitHub-Delivery") ?? "";
    const dedupKey = `check:${deliveryId}:${payload.comment.id}`;
    const existing = await env.DEDUP_KV.get(dedupKey);
    if (existing) {
      return new Response("Already processed", { status: 200 });
    }

    // 5. Enqueue pipeline job BEFORE writing KV.
    // If queue send fails, no KV entry → GitHub retries cleanly.
    // If queue send succeeds but KV put fails, worst case is a
    // duplicate that hasExistingReview() catches in the consumer.
    const job: PipelineJob = {
      repo: payload.repository.full_name,
      prNumber: payload.issue.number,
      diffUrl: payload.issue.pull_request.diff_url,
    };
    await env.PIPELINE_QUEUE.send(job);
    await env.DEDUP_KV.put(dedupKey, "processing", {
      expirationTtl: 86400,
    });

    return new Response("Accepted", { status: 202 });
  },

  /**
   * Queue consumer — processes pipeline jobs with 15 minutes wall clock time.
   *
   * This is where the heavy work happens: fetch diff, run 3-phase Claude
   * pipeline (extract → fact-check with Brave → editorial review), post
   * review comment on the PR.
   *
   * Failed messages are retried up to 2 times by the Queue (see wrangler.toml).
   */
  async queue(
    batch: MessageBatch<PipelineJob>,
    env: Env
  ): Promise<void> {
    for (const message of batch.messages) {
      try {
        await processJob(message.body, env);
        message.ack();
      } catch (err) {
        const raw = err instanceof Error ? err.message : String(err);
        const safe = raw
          .replace(/sk-[a-zA-Z0-9-]+/g, "[REDACTED]")
          .replace(/token [a-zA-Z0-9_-]+/gi, "token [REDACTED]")
          .slice(0, 200);

        // Post error to PR before retrying.
        // Uses ERROR_MARKER (not MARKER) so hasExistingReview() doesn't
        // mistake an error comment for a successful review — retries must
        // be able to proceed after a prior failure.
        await postPrComment(
          message.body.repo,
          message.body.prNumber,
          `${ERROR_MARKER}\nArticle check encountered an error. Retrying automatically.\n\n<details><summary>Details</summary>\n\n\`${safe}\`\n</details>`,
          env.GITHUB_TOKEN
        ).catch(() => {});

        message.retry();
      }
    }
  },
};

async function processJob(job: PipelineJob, env: Env): Promise<void> {
  const { repo, prNumber, diffUrl } = job;

  // Check for existing bot review to avoid duplicate comments
  const alreadyReviewed = await hasExistingReview(
    repo,
    prNumber,
    env.GITHUB_TOKEN
  );
  if (alreadyReviewed) return;

  // Fetch and parse the PR diff
  const rawDiff = await fetchPrDiff(diffUrl, env.GITHUB_TOKEN);
  const files = parseDiff(rawDiff);

  // Extract article text (first file, first hunk — matching Python behavior)
  const articleText = extractArticleText(files);
  if (!articleText || articleText.trim().length < 20) {
    await postPrComment(
      repo,
      prNumber,
      `${MARKER}\nNo article content found in this PR.`,
      env.GITHUB_TOKEN
    );
    return;
  }

  // Run the 3-phase pipeline
  const model = env.ANTHROPIC_MODEL;
  const maxTokens = env.ANTHROPIC_MAX_TOKENS
    ? parseInt(env.ANTHROPIC_MAX_TOKENS, 10)
    : undefined;

  const review = await runPipeline(
    articleText,
    env.ANTHROPIC_API_KEY,
    env.BRAVE_API_KEY,
    model,
    maxTokens
  );

  // Post the review comment
  const comment = `${MARKER}\n## Article Check Results\n\n${review}`;
  await postPrComment(repo, prNumber, comment, env.GITHUB_TOKEN);
}
