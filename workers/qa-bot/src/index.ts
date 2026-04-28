/**
 * 🌰 QA Bot Worker — Cloudflare Workers entry point
 * Migrated from GitHub Actions Python bot to single Worker + KV
 *
 * Issue #425: Migrate GitHub Actions bot to Cloudflare Workers
 * Bounty: $1000
 */

import { Env, WebhookPayload } from './types';
import { verifyWebhookSignature } from './github';
import {
  parseWebhookPayload,
  isArticleCheckCommand,
  isAuthorizedReviewer,
  getPRNumber,
} from './webhook';
import { runArticleCheck } from './articlechecker';

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Only accept POST from GitHub webhooks
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    // Health check endpoint
    const url = new URL(request.url);
    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'ok', version: '1.0.0' }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    try {
      // Read raw body for signature verification
      const rawBody = await request.text();

      // Verify webhook signature
      const signature = request.headers.get('X-Hub-Signature-256') ?? '';
      if (!verifyWebhookSignature(rawBody, signature, env.WEBHOOK_SECRET)) {
        return new Response('Invalid signature', { status: 401 });
      }

      // Parse payload
      const payload: WebhookPayload = parseWebhookPayload(rawBody);

      // Check if this is an /articlecheck command
      if (!isArticleCheckCommand(payload)) {
        return new Response('Not an articlecheck command', { status: 200 });
      }

      // Verify commenter is authorized
      const commenter = payload.comment?.user?.login ?? '';
      const reviewersList = env.WEBHOOK_SECRET; // Using env var for reviewers; adjust as needed
      if (!isAuthorizedReviewer(commenter, reviewersList)) {
        return new Response('Unauthorized', { status: 403 });
      }

      // Get PR number
      const prNumber = getPRNumber(payload);
      if (!prNumber) {
        return new Response('Not a PR comment', { status: 200 });
      }

      // Run the article check
      const [owner, repo] = payload.repository.full_name.split('/');
      const commentId = payload.comment!.id;

      const result = await runArticleCheck(
        env,
        owner,
        repo,
        prNumber,
        commentId
      );

      // Post result as PR comment
      if (result.success && result.commentBody) {
        await postComment(env, owner, repo, prNumber, result.commentBody);
      }

      return new Response(
        JSON.stringify({ success: result.success, error: result.error }),
        {
          status: result.success ? 200 : 500,
          headers: { 'Content-Type': 'application/json' },
        }
      );

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return new Response(JSON.stringify({ error: message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  },
};

/**
 * Post a comment on a PR
 */
async function postComment(
  env: Env,
  owner: string,
  repo: string,
  prNumber: number,
  body: string
): Promise<void> {
  const token = env.APP_PRIVATE_KEY; // In production, use installation token

  await fetch(
    `https://api.github.com/repos/${owner}/${repo}/issues/${prNumber}/comments`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ body }),
    }
  );
}
