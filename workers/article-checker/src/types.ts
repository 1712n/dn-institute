/**
 * Environment bindings for the Cloudflare Worker.
 * Secrets are configured via `wrangler secret put`.
 * Variables are set in wrangler.toml under [vars].
 */
export interface Env {
  // Secrets
  GITHUB_TOKEN: string;
  GITHUB_WEBHOOK_SECRET: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  WIKI_REVIEWERS: string; // JSON array of allowed GitHub usernames

  // Variables (from wrangler.toml [vars])
  ANTHROPIC_SEARCH_MODEL: string;
  ANTHROPIC_SEARCH_TEMPERATURE: string;
  ANTHROPIC_SEARCH_MAX_TOKENS: string;
  ANTHROPIC_SUMMARIZE_MODEL: string;
  ANTHROPIC_SUMMARIZE_TEMPERATURE: string;
  ANTHROPIC_SUMMARIZE_MAX_TOKENS: string;
  GITHUB_REPO: string;
}

/** A parsed diff file from a pull request */
export interface DiffFile {
  header: string;
  body: DiffSegment[];
}

/** A segment within a parsed diff */
export interface DiffSegment {
  header: string;
  body: string;
}

/** A single search result from Brave Search */
export interface SearchResult {
  content: string;
  url: string;
}

/** GitHub webhook payload for issue_comment events */
export interface IssueCommentPayload {
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

/** Anthropic Messages API request */
export interface AnthropicMessage {
  role: "user" | "assistant";
  content: AnthropicContent[];
}

export interface AnthropicContent {
  type: "text";
  text: string;
}

/** Anthropic Messages API response */
export interface AnthropicResponse {
  content: AnthropicContent[];
  stop_reason: string | null;
  stop_sequence: string | null;
}
