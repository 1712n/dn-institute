/**
 * Environment bindings for the QA Bot Worker.
 * Secrets are set via `wrangler secret put <NAME>`.
 */
export type Env = {
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;
  BRAVE_API_KEY: string;
  ANTHROPIC_MODEL: string;
  ANTHROPIC_MAX_TOKENS: string;
};

/** GitHub webhook payload for issue_comment events */
export interface IssueCommentPayload {
  action: string;
  comment: {
    body: string;
    user: { login: string };
  };
  issue: {
    number: number;
    pull_request?: {
      url: string;
      diff_url: string;
    };
  };
  repository: {
    full_name: string;
  };
}

/** GitHub webhook payload for pull_request events */
export interface PullRequestPayload {
  action: string;
  number: number;
  pull_request: {
    url: string;
    diff_url: string;
    number: number;
  };
  repository: {
    full_name: string;
  };
}

/** Parsed diff segment */
export interface DiffFile {
  filename: string;
  additions: string;
}

/** Brave Search API response types */
export interface BraveSearchResult {
  title: string;
  url: string;
  description: string;
}

export interface BraveSearchResponse {
  web?: {
    results: BraveSearchResult[];
  };
}

/** Claude Messages API types */
export interface ClaudeMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ClaudeResponse {
  content: Array<{
    type: string;
    text: string;
  }>;
  stop_reason: string | null;
  stop_sequence: string | null;
}
