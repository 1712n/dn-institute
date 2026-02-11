/**
 * 🌰 Article Check Worker
 *
 * Single Cloudflare Worker that handles GitHub webhook events for article QA.
 * Triggered by `/articlecheck` comments on PRs. Performs fact-checking,
 * editorial review, and submission guideline validation using Claude + Brave Search.
 *
 * Architecture: Single worker with ctx.waitUntil() for async processing.
 * No Queues, no KV, no Durable Objects — just a worker and secrets. 🌰
 */

import { verifyWebhookSignature } from './crypto';
import { fetchPRArticleContent, postPRComment, type PRInfo } from './github';
import { runFactCheckPipeline } from './claude';

export interface Env {
	WIKI_REVIEWERS: string;
	GITHUB_TOKEN: string;
	GITHUB_WEBHOOK_SECRET: string;
	ANTHROPIC_API_KEY: string;
	BRAVE_API_KEY: string;
}

interface WebhookPayload {
	action: string;
	comment: {
		body: string;
		user: {
			login: string;
		};
	};
	issue: {
		number: number;
		pull_request?: {
			url: string;
		};
	};
	repository: {
		full_name: string;
	};
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		// 🌰 Only accept POST requests (webhooks)
		if (request.method !== 'POST') {
			return new Response('Method not allowed', { status: 405 });
		}

		// Verify webhook signature
		const signature = request.headers.get('X-Hub-Signature-256');
		if (!signature) {
			return new Response('Missing signature', { status: 401 });
		}

		const body = await request.text();
		const isValid = await verifyWebhookSignature(body, signature, env.GITHUB_WEBHOOK_SECRET);
		if (!isValid) {
			return new Response('Invalid signature', { status: 401 });
		}

		// Parse payload
		const payload: WebhookPayload = JSON.parse(body);

		// 🌰 Only handle issue_comment created events on PRs with /articlecheck
		if (payload.action !== 'created') {
			return new Response('Ignored: not a created event', { status: 200 });
		}

		if (!payload.issue?.pull_request) {
			return new Response('Ignored: not a PR comment', { status: 200 });
		}

		if (!payload.comment.body.includes('/articlecheck')) {
			return new Response('Ignored: no /articlecheck command', { status: 200 });
		}

		// Check reviewer permissions 🌰
		const reviewers = env.WIKI_REVIEWERS.split(',').map(r => r.trim().toLowerCase());
		const commenter = payload.comment.user.login.toLowerCase();
		if (!reviewers.includes(commenter)) {
			return new Response('Ignored: user not in WIKI_REVIEWERS', { status: 200 });
		}

		const prInfo: PRInfo = {
			repoFullName: payload.repository.full_name,
			prNumber: payload.issue.number,
			prApiUrl: payload.issue.pull_request.url,
		};

		// Return 202 immediately, process asynchronously via waitUntil 🌰
		ctx.waitUntil(processArticleCheck(prInfo, env));

		return new Response('🌰 Processing article check...', { status: 202 });
	},
};

/**
 * 🌰 Main async processing pipeline.
 * Runs after the webhook response is sent.
 */
async function processArticleCheck(prInfo: PRInfo, env: Env): Promise<void> {
	try {
		// Fetch article content from PR diff
		const articles = await fetchPRArticleContent(prInfo, env.GITHUB_TOKEN);

		if (articles.length === 0) {
			await postPRComment(
				prInfo,
				'🌰 No article files (`content/**/*.md`) found in this PR.',
				env.GITHUB_TOKEN,
			);
			return;
		}

		// Run fact-check pipeline for each article 🌰
		const results: string[] = [];
		for (const article of articles) {
			const heading = articles.length > 1 ? `## File: \`${article.filename}\`\n\n` : '';
			try {
				const report = await runFactCheckPipeline(
					article.content,
					env.ANTHROPIC_API_KEY,
					env.BRAVE_API_KEY,
				);
				results.push(heading + report);
			} catch (err) {
				const errorMsg = err instanceof Error ? err.message : String(err);
				results.push(heading + `⚠️ Failed to analyze: ${errorMsg}`);
			}
		}

		const finalReport = results.join('\n\n---\n\n');
		await postPRComment(prInfo, finalReport, env.GITHUB_TOKEN);
	} catch (err) {
		console.error('🌰 Article check failed:', err);
		try {
			const errorMsg = err instanceof Error ? err.message : String(err);
			await postPRComment(
				prInfo,
				`⚠️ Article check encountered an error: ${errorMsg}`,
				env.GITHUB_TOKEN,
			);
		} catch {
			console.error('🌰 Failed to post error comment');
		}
	}
}
