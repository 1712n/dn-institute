import type { PrFile, WebhookPayload } from "./types"

const GITHUB_API = "https://api.github.com"

/**
 * Parse the list of authorized reviewers from the WIKI_REVIEWERS secret.
 * Accepts a JSON array of strings, e.g. '["user1","user2"]'.
 */
export function parseReviewers(raw: string): string[] {
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      return parsed.filter((s): s is string => typeof s === "string")
    }
  } catch {
    // fall through
  }
  return []
}

/**
 * Check whether a comment triggers the article check command.
 */
export function isArticleCheckCommand(commentBody: string): boolean {
  return commentBody.trim().startsWith("/articlecheck")
}

/**
 * Check whether the commenter is on a pull request (not a plain issue).
 */
export function isPullRequestComment(payload: WebhookPayload): boolean {
  return payload.issue.pull_request !== undefined
}

/**
 * Fetch the list of changed files in a pull request.
 */
export async function fetchPrFiles(
  repo: string,
  prNumber: number,
  token: string
): Promise<PrFile[]> {
  const url = `${GITHUB_API}/repos/${repo}/pulls/${prNumber}/files`
  const resp = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "User-Agent": "articlecheck-worker"
    }
  })

  if (!resp.ok) {
    throw new Error(`GitHub API error ${resp.status}: ${await resp.text()}`)
  }

  return resp.json() as Promise<PrFile[]>
}

/**
 * Fetch the raw diff for a pull request.
 */
export async function fetchPrDiff(
  repo: string,
  prNumber: number,
  token: string
): Promise<string> {
  const url = `${GITHUB_API}/repos/${repo}/pulls/${prNumber}`
  const resp = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "articlecheck-worker"
    }
  })

  if (!resp.ok) {
    throw new Error(`GitHub API error ${resp.status}: ${await resp.text()}`)
  }

  return resp.text()
}

/**
 * Fetch raw content of a file at a specific ref from GitHub.
 */
export async function fetchFileContent(
  repo: string,
  path: string,
  ref: string,
  token: string
): Promise<string> {
  const url = `${GITHUB_API}/repos/${repo}/contents/${path}?ref=${ref}`
  const resp = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.raw",
      "User-Agent": "articlecheck-worker"
    }
  })

  if (!resp.ok) {
    throw new Error(
      `Failed to fetch ${path}: ${resp.status} ${await resp.text()}`
    )
  }

  return resp.text()
}

/**
 * Fetch the head SHA for a pull request.
 */
export async function fetchPrHead(
  repo: string,
  prNumber: number,
  token: string
): Promise<string> {
  const url = `${GITHUB_API}/repos/${repo}/pulls/${prNumber}`
  const resp = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "User-Agent": "articlecheck-worker"
    }
  })

  if (!resp.ok) {
    throw new Error(`GitHub API error ${resp.status}: ${await resp.text()}`)
  }

  const data = (await resp.json()) as { head: { sha: string } }
  return data.head.sha
}

/**
 * Post a comment on a pull request (via the issues API).
 */
export async function postComment(
  repo: string,
  issueNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `${GITHUB_API}/repos/${repo}/issues/${issueNumber}/comments`
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "User-Agent": "articlecheck-worker",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ body })
  })

  if (!resp.ok) {
    throw new Error(
      `Failed to post comment: ${resp.status} ${await resp.text()}`
    )
  }
}
