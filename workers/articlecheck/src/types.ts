export interface Env {
  WEBHOOK_SECRET: string
  GITHUB_TOKEN: string
  ANTHROPIC_API_KEY: string
  BRAVE_API_KEY: string
  WIKI_REVIEWERS: string
}

export interface WebhookPayload {
  action: string
  comment: {
    body: string
    user: {
      login: string
    }
    id: number
  }
  issue: {
    number: number
    pull_request?: {
      url: string
      diff_url: string
      html_url: string
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

export interface PrFile {
  filename: string
  status: string
  raw_url: string
  patch?: string
}

export interface SearchResult {
  title: string
  url: string
  description: string
}

export interface ClaudeMessage {
  role: "user" | "assistant"
  content: string
}
