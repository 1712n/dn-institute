/** Environment bindings for the Cloudflare Worker */
export type Env = {
  /** Anthropic API key for Claude */
  LLM_API_KEY: string
  /** Brave Search API key */
  SEARCH_API_KEY: string
  /** GitHub token for posting PR comments */
  GITHUB_TOKEN: string
  /** GitHub webhook secret for signature verification */
  WEBHOOK_SECRET: string
  /** JSON array of authorized reviewer GitHub usernames */
  WIKI_REVIEWERS: string
}

/** GitHub webhook payload for issue_comment events */
export interface IssueCommentEvent {
  action: string
  issue: {
    number: number
    pull_request?: {
      url: string
      diff_url: string
      html_url: string
    }
  }
  comment: {
    body: string
    user: {
      login: string
    }
  }
  repository: {
    full_name: string
    owner: {
      login: string
    }
    name: string
  }
}

/** Parsed diff file structure */
export interface DiffFile {
  header: string
  body: DiffSegment[]
}

export interface DiffSegment {
  header: string
  body: string
}

/** Search result from Brave API */
export interface BraveSearchResult {
  url: string
  content: string
}

/** Claude API message structure */
export interface ClaudeMessage {
  role: "user" | "assistant"
  content: Array<{ type: "text"; text: string }>
}

/** Claude API response */
export interface ClaudeResponse {
  content: Array<{ type: "text"; text: string }>
  stop_reason: string | null
  stop_sequence: string | null
}
