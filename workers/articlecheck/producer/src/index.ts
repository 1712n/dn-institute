import { parseReviewerAllowlist } from "../../common/src/allowlist";
import { logger } from "../../common/src/log";
import type { IssueCommentCreatedEvent } from "../../common/src/github/events";
import { readGitHubWebhookHeaders, verifyGitHubWebhookSignature } from "../../common/src/github/webhook";
import type { ArticleCheckJob } from "../../common/src/job";

export type Env = {
  GITHUB_WEBHOOK_SECRET?: string;
  WIKI_REVIEWERS?: string;
  ARTICLECHECK_QUEUE: Queue<ArticleCheckJob>;
};

function isArticleCheckCommand(body: string): boolean {
  return body.includes("/articlecheck");
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

    const headers = readGitHubWebhookHeaders(request.headers);
    const rawBody = await request.arrayBuffer();

    const sig = await verifyGitHubWebhookSignature({
      headers,
      secret: env.GITHUB_WEBHOOK_SECRET,
      rawBody
    });
    if (!sig.ok) {
      logger.warn("github_webhook_signature_rejected", {
        reason: sig.reason,
        delivery_id: headers.deliveryId,
        event: headers.event
      });
      return new Response("Unauthorized", { status: 401 });
    }

    if (headers.event !== "issue_comment") return new Response("Ignored", { status: 200 });

    let payload: IssueCommentCreatedEvent;
    try {
      payload = JSON.parse(new TextDecoder().decode(rawBody)) as IssueCommentCreatedEvent;
    } catch (err) {
      logger.warn("bad_json_payload", { delivery_id: headers.deliveryId, err: String(err) });
      return new Response("Bad Request", { status: 400 });
    }

    const deliveryId = headers.deliveryId;
    if (!deliveryId) {
      // Not expected from GitHub, but keep behavior explicit.
      logger.warn("missing_delivery_id");
      return new Response("Bad Request", { status: 400 });
    }

    if (payload.action !== "created") return new Response("Ignored", { status: 200 });
    if (!payload.issue.pull_request) return new Response("Ignored", { status: 200 });
    if (!isArticleCheckCommand(payload.comment.body)) return new Response("Ignored", { status: 200 });

    const allowlist = parseReviewerAllowlist(env.WIKI_REVIEWERS);
    const actor = payload.sender.login.toLowerCase();
    if (!allowlist.has(actor)) {
      logger.info("actor_not_allowlisted", { actor, delivery_id: deliveryId });
      return new Response("Ignored", { status: 200 });
    }

    const installationId = payload.installation?.id;
    if (!installationId) {
      // With GitHub App webhooks, this should be present. Fail closed (no expensive work).
      logger.warn("missing_installation_id", { delivery_id: deliveryId, repo: payload.repository.full_name });
      return new Response("Ignored", { status: 200 });
    }

    const job: ArticleCheckJob = {
      delivery_id: deliveryId,
      repo_full_name: payload.repository.full_name,
      pr_number: payload.issue.number,
      comment_id: payload.comment.id,
      actor,
      installation_id: installationId
    };

    ctx.waitUntil(
      (async () => {
        await env.ARTICLECHECK_QUEUE.send(job);
        logger.info("queued_articlecheck_job", {
          delivery_id: deliveryId,
          repo: job.repo_full_name,
          pr_number: job.pr_number,
          comment_id: job.comment_id,
          actor: job.actor
        });
      })()
    );

    // GitHub expects a response within ~10s. Queueing lets us return fast.
    return new Response("Accepted", { status: 202 });
  }
};
