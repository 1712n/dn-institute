/**
 * dn-institute article-check Cloudflare Worker.
 *
 * Replaces the GHA bot at .github/workflows/article-check-claude.yml that runs
 * tools/article_checker/article_checker_claude.py. Same purpose: validate that
 * a new Crypto Attack Wiki article PR complies with submission guidelines, do
 * fact-checking via Brave Search + Claude, post a markdown report as a PR
 * comment.
 *
 * Trigger: GitHub webhook event "issue_comment" with action "created" where
 * the comment body contains "/articlecheck" AND the comment author is in
 * WIKI_REVIEWERS.
 *
 * Architecture:
 *   1. Verify HMAC-SHA256 signature on the webhook (X-Hub-Signature-256).
 *   2. Filter to relevant events.
 *   3. Permission check: commenter must be in WIKI_REVIEWERS list.
 *   4. Fetch PR diff via GitHub API.
 *   5. ctx.waitUntil() the long-running LLM checks (30-60s budget).
 *   6. Return 202 to GitHub within seconds so the webhook does not retry.
 *   7. After checks complete, post a comment on the PR with the report.
 */
import { runArticleChecks } from "./checker";
import { fetchPullRequestDiff, postPullRequestComment } from "./github";
import { verifyWebhookSignature } from "./signature";

export interface Env {
  GITHUB_APP_TOKEN: string;
  WEBHOOK_SECRET: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  WIKI_REVIEWERS: string;
}

interface IssueCommentEvent {
  action: string;
  comment: { body: string; user: { login: string } };
  issue: {
    number: number;
    pull_request?: { url: string };
  };
  repository: { full_name: string };
}

const TRIGGER = "/articlecheck";

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
    if (request.headers.get("X-GitHub-Event") !== "issue_comment") {
      return new Response("Ignored: not an issue_comment event", { status: 200 });
    }

    const rawBody = await request.text();
    const sig = request.headers.get("X-Hub-Signature-256") ?? "";
    if (!(await verifyWebhookSignature(env.WEBHOOK_SECRET, rawBody, sig))) {
      return new Response("Bad signature", { status: 401 });
    }

    const event = JSON.parse(rawBody) as IssueCommentEvent;
    if (event.action !== "created") return new Response("Ignored: not created", { status: 200 });
    if (!event.issue.pull_request) return new Response("Ignored: not a PR", { status: 200 });
    if (!event.comment.body.includes(TRIGGER)) {
      return new Response(`Ignored: no ${TRIGGER} trigger`, { status: 200 });
    }

    let reviewers: string[];
    try {
      reviewers = JSON.parse(env.WIKI_REVIEWERS);
    } catch {
      return new Response("WIKI_REVIEWERS misconfigured", { status: 500 });
    }
    if (!reviewers.includes(event.comment.user.login)) {
      return new Response("Ignored: commenter not in WIKI_REVIEWERS", { status: 200 });
    }

    ctx.waitUntil(handleCheckRequest(env, event));
    return new Response("Accepted", { status: 202 });
  },
};

async function handleCheckRequest(env: Env, event: IssueCommentEvent): Promise<void> {
  const repoFullName = event.repository.full_name;
  const prNumber = event.issue.number;
  try {
    const diff = await fetchPullRequestDiff(env.GITHUB_APP_TOKEN, repoFullName, prNumber);
    const report = await runArticleChecks({
      diff,
      anthropicApiKey: env.ANTHROPIC_API_KEY,
      braveApiKey: env.BRAVE_API_KEY,
    });
    await postPullRequestComment(env.GITHUB_APP_TOKEN, repoFullName, prNumber, report);
  } catch (err) {
    console.error("article-check failed:", err);
    await postPullRequestComment(
      env.GITHUB_APP_TOKEN,
      repoFullName,
      prNumber,
      `:warning: article-check encountered an error: ${(err as Error).message}`,
    ).catch(() => {});
  }
}
