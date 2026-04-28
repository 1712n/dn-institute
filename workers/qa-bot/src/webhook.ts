/**
 * 🌰 Webhook event parsing and validation
 */

import { WebhookPayload } from './types';

export class WebhookError extends Error {
  constructor(message: string, public status: number = 400) {
    super(message);
    this.name = 'WebhookError';
  }
}

/**
 * Parse and validate incoming webhook payload
 */
export function parseWebhookPayload(body: string): WebhookPayload {
  try {
    const payload = JSON.parse(body) as WebhookPayload;
    validatePayload(payload);
    return payload;
  } catch (e) {
    if (e instanceof WebhookError) throw e;
    throw new WebhookError('Invalid JSON payload', 400);
  }
}

/**
 * Validate required fields in webhook payload
 */
function validatePayload(payload: WebhookPayload): void {
  if (!payload.action) {
    throw new WebhookError('Missing required field: action', 400);
  }

  if (!payload.repository?.full_name) {
    throw new WebhookError('Missing required field: repository.full_name', 400);
  }
}

/**
 * Check if this is an article check command
 */
export function isArticleCheckCommand(payload: WebhookPayload): boolean {
  if (payload.action !== 'created' && payload.action !== 'edited') {
    return false;
  }

  const body = payload.comment?.body?.trim() ?? '';
  return body.startsWith('/articlecheck');
}

/**
 * Extract the command arguments from comment body
 */
export function extractCommandArgs(body: string): string[] {
  const parts = body.trim().split(/\s+/);
  // First part is the command itself
  return parts.slice(1);
}

/**
 * Check if commenter is in WIKI_REVIEWERS list
 * In production, this would check against a configured list or team membership
 */
export function isAuthorizedReviewer(
  username: string,
  reviewersList: string
): boolean {
  if (!reviewersList) {
    // If no reviewers configured, allow all (dev mode)
    return true;
  }

  const reviewers = reviewersList
    .split(',')
    .map(r => r.trim().toLowerCase());

  return reviewers.includes(username.toLowerCase());
}

/**
 * Get PR number from webhook payload
 */
export function getPRNumber(payload: WebhookPayload): number | null {
  // For issue_comment on PRs, the issue number IS the PR number
  if (payload.issue?.pull_request) {
    return payload.issue.number;
  }
  return null;
}
