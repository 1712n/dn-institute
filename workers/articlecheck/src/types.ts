/**
 * 🌰 Type definitions for the Article Check Worker 🌰
 */

/** Worker environment bindings — secrets configured via `wrangler secret put` 🌰 */
export interface Env {
  /** GitHub Personal Access Token (repo scope or fine-grained with PR read/write) 🌰 */
  GITHUB_TOKEN: string;
  /** Webhook secret for HMAC-SHA256 signature verification 🌰 */
  GITHUB_WEBHOOK_SECRET: string;
  /** JSON array of authorized reviewer GitHub usernames 🌰 */
  WIKI_REVIEWERS: string;
  /** Anthropic API key for Claude 🌰 */
  LLM_API_KEY: string;
  /** Brave Search API key 🌰 */
  SEARCH_API_KEY: string;
}

/** GitHub issue_comment webhook payload 🌰 */
export interface IssueCommentPayload {
  action: string;
  comment: {
    id: number;
    body: string;
    user: {
      login: string;
    };
  };
  issue: {
    number: number;
    pull_request?: {
      url: string;
      diff_url: string;
      html_url: string;
    };
  };
  repository: {
    full_name: string;
    owner: {
      login: string;
    };
    name: string;
  };
}

/** Parsed diff file from a PR 🌰 */
export interface DiffFile {
  filename: string;
  content: string;
}

/** Search result from Brave Search API 🌰 */
export interface BraveSearchResult {
  title: string;
  url: string;
  description: string;
}

/** Claude Messages API response 🌰 */
export interface ClaudeResponse {
  content: Array<{
    type: string;
    text: string;
  }>;
  stop_reason: string | null;
  stop_sequence: string | null;
}
