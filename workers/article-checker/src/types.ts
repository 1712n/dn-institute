// 🌰 Type definitions for the Article Checker Worker 🌰

/** 🌰 Environment bindings for the Cloudflare Worker */
export interface Env {
  GITHUB_TOKEN: string;
  GITHUB_WEBHOOK_SECRET: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_SEARCH_API_KEY: string;
  /** JSON array of authorized reviewer GitHub usernames */
  WIKI_REVIEWERS: string;
}

/** 🌰 Parsed file from a unified diff */
export interface DiffFile {
  header: string;
  body: DiffSegment[];
}

/** 🌰 A segment within a diff file */
export interface DiffSegment {
  header: string;
  body: string;
}

/** 🌰 GitHub webhook payload for issue_comment events */
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

/** 🌰 Brave Search API response types */
export interface BraveSearchResponse {
  mixed?: {
    main: Array<{ type: string; index?: number }>;
  };
  web?: {
    results: BraveWebResult[];
  };
  news?: {
    results: BraveNewsResult[];
  };
  faq?: {
    results: BraveFaqResult[];
  };
}

export interface BraveWebResult {
  title: string;
  url: string;
  description: string;
}

export interface BraveNewsResult {
  title: string;
  url: string;
  description: string;
  age?: string;
  meta_url?: { hostname: string };
}

export interface BraveFaqResult {
  title: string;
  url: string;
  question: string;
  answer: string;
}

/** 🌰 Claude Messages API types */
export interface ClaudeMessage {
  role: "user" | "assistant";
  content: string | ClaudeContentBlock[];
}

export interface ClaudeContentBlock {
  type: "text";
  text: string;
}

export interface ClaudeResponse {
  content: ClaudeContentBlock[];
  stop_reason: string | null;
  stop_sequence: string | null;
}
