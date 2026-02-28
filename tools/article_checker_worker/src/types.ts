/**
 * 🌰 Type definitions for Article Checker Worker
 */

export interface Env {
  WEBHOOK_SECRET: string
  GITHUB_TOKEN: string
  ANTHROPIC_API_KEY: string
  BRAVE_API_KEY: string
  REVIEWER_ALLOWLIST?: string
}

export interface GitHubWebhookPayload {
  action: string
  issue?: {
    number: number
    pull_request?: {
      url: string
    }
  }
  comment?: {
    id: number
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
  sender: {
    login: string
  }
}

export interface PullRequestInfo {
  owner: string
  repo: string
  number: number
  diff: string
}

export interface DiffFile {
  filename: string
  header: string
  body: string
}

export interface SearchResult {
  url: string
  content: string
}

export interface ClaudeMessage {
  role: "user" | "assistant"
  content: Array<{ type: "text"; text: string }>
}

export interface ClaudeResponse {
  content: Array<{ type: "text"; text: string }>
  stop_reason: string
  stop_sequence: string | null
}

export interface BraveSearchResponse {
  mixed?: {
    main?: Array<{ type: string; index?: number }>
  }
  web?: {
    results?: Array<{
      title: string
      url: string
      description: string
    }>
  }
  news?: {
    results?: Array<{
      title: string
      url: string
      description: string
      age?: string
      meta_url?: { hostname?: string }
    }>
  }
  faq?: {
    results?: Array<{
      title: string
      url: string
      question: string
      answer: string
    }>
  }
}
