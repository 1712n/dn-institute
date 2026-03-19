export type Env = {
  ANTHROPIC_API_KEY: string
  BRAVE_SEARCH_API_KEY: string
  GITHUB_TOKEN: string
  WEBHOOK_SECRET: string
  WIKI_REVIEWERS: string // JSON array of GitHub usernames
}

export interface GitHubWebhookPayload {
  action: string
  comment: {
    body: string
    user: { login: string }
  }
  issue: {
    number: number
    pull_request?: { url: string; diff_url: string; html_url: string }
  }
  repository: {
    full_name: string
  }
}

export interface DiffFile {
  filename: string
  content: string
}

export interface SearchResult {
  title: string
  url: string
  content: string
}

export interface FactCheckResult {
  statement: string
  verdict: 'true' | 'false' | 'unverified'
  source: string
  explanation: string
}
