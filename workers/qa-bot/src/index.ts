/**
 * dn-institute QA Bot — Cloudflare Worker
 *
 * Receives GitHub webhook events for PRs and issue comments,
 * checks article quality against submission guidelines using Claude,
 * and posts review comments back to the PR.
 */

import { verifyWebhookSignature } from "./crypto";
import { handlePRCheck } from "./handler";

export interface Env {
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;
  /** Comma-separated list of GitHub usernames allowed to trigger checks */
  WIKI_REVIEWERS: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    const body = await request.text();

    // Verify webhook signature
    const signature = request.headers.get("x-hub-signature-256");
    if (!signature || !(await verifyWebhookSignature(body, signature, env.GITHUB_WEBHOOK_SECRET))) {
      return new Response("Invalid signature", { status: 401 });
    }

    const event = request.headers.get("x-github-event");
    const payload = JSON.parse(body);

    // Handle issue_comment events (same trigger as the original bot)
    if (event === "issue_comment" && payload.action === "created") {
      const comment: string = payload.comment?.body ?? "";
      const isPR = !!payload.issue?.pull_request;

      if (!isPR || !comment.includes("/articlecheck")) {
        return new Response("Ignored: not a PR comment or missing /articlecheck command", { status: 200 });
      }

      // Permission check
      const reviewers: string[] = env.WIKI_REVIEWERS.split(",").map((s) => s.trim().toLowerCase());
      const actor = (payload.comment?.user?.login ?? "").toLowerCase();
      if (!reviewers.includes(actor)) {
        return new Response("Ignored: user not authorized", { status: 200 });
      }

      const prUrl: string = payload.issue.pull_request.url;

      // Process asynchronously using waitUntil-style pattern
      // (Cloudflare Workers support up to 30s CPU / 6min wall-clock on paid plan)
      try {
        await handlePRCheck(prUrl, env);
        return new Response("OK", { status: 200 });
      } catch (err: any) {
        console.error("Error processing PR check:", err);
        return new Response("Internal error", { status: 500 });
      }
    }

    // Also support pull_request events for automatic checks on PR open/sync
    if (event === "pull_request" && (payload.action === "opened" || payload.action === "synchronize")) {
      const prUrl: string = payload.pull_request?.url;
      if (!prUrl) {
        return new Response("Missing PR URL", { status: 400 });
      }

      try {
        await handlePRCheck(prUrl, env);
        return new Response("OK", { status: 200 });
      } catch (err: any) {
        console.error("Error processing PR check:", err);
        return new Response("Internal error", { status: 500 });
      }
    }

    return new Response("Event not handled", { status: 200 });
  },
};
