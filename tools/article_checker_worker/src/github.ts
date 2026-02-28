/**
 * 🌰 GitHub API interactions — PR diff fetching, comment posting, allowlist
 */

import type { DiffFile, GitHubWebhookPayload, PullRequestInfo } from "./types"

const DEFAULT_REVIEWERS = ["evgenydmitriev"]

/**
 * Check if a user is in the reviewer allowlist.
 */
export function isAllowedReviewer(
  username: string,
  allowlistJson?: string
): boolean {
  let allowlist: string[] = DEFAULT_REVIEWERS
  if (allowlistJson) {
    try {
      const parsed = JSON.parse(allowlistJson)
      if (Array.isArray(parsed)) {
        allowlist = parsed
      }
    } catch {
      // Fall back to default if JSON is invalid
    }
  }
  return allowlist.includes(username)
}

/**
 * Validate that the webhook payload is an /articlecheck comment on a PR.
 */
export function validateWebhookPayload(
  payload: GitHubWebhookPayload
): { valid: true; prNumber: number; prUrl: string } | { valid: false; reason: string } {
  if (payload.action !== "created") {
    return { valid: false, reason: "Not a comment creation event" }
  }

  if (!payload.issue?.pull_request) {
    return { valid: false, reason: "Comment is not on a pull request" }
  }

  if (!payload.comment?.body?.includes("/articlecheck")) {
    return { valid: false, reason: "Comment does not contain /articlecheck" }
  }

  return {
    valid: true,
    prNumber: payload.issue.number,
    prUrl: payload.issue.pull_request.url,
  }
}

/**
 * Fetch the diff for a pull request.
 */
export async function fetchPRDiff(
  owner: string,
  repo: string,
  prNumber: number,
  token: string
): Promise<string> {
  const url = `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}`
  const response = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "article-checker-worker",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch PR diff: ${response.status} ${response.statusText}`)
  }

  return response.text()
}

/**
 * Parse a unified diff into structured file objects.
 * Extracts added content from the diff (lines starting with +).
 */
export function parseDiff(rawDiff: string): DiffFile[] {
  const files: DiffFile[] = []
  const fileSections = rawDiff.split(/^diff --git /m).filter(Boolean)

  for (const section of fileSections) {
    const lines = section.split("\n")
    const headerMatch = lines[0]?.match(/a\/(.*?) b\/(.*)/)
    if (!headerMatch) continue

    const filename = headerMatch[2]

    // Only process content files (markdown under content/)
    if (!filename.endsWith(".md")) continue

    // Extract the added lines (lines starting with +, excluding +++ header)
    const addedLines: string[] = []
    let inHunk = false

    for (const line of lines) {
      if (line.startsWith("@@")) {
        inHunk = true
        continue
      }
      if (inHunk && line.startsWith("+") && !line.startsWith("+++")) {
        addedLines.push(line.substring(1))
      }
    }

    if (addedLines.length > 0) {
      files.push({
        filename,
        header: `--- a/${filename}\n+++ b/${filename}`,
        body: addedLines.join("\n"),
      })
    }
  }

  return files
}

/**
 * Post a comment on a pull request.
 */
export async function postPRComment(
  owner: string,
  repo: string,
  prNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `https://api.github.com/repos/${owner}/${repo}/issues/${prNumber}/comments`
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "article-checker-worker",
    },
    body: JSON.stringify({ body }),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Failed to post PR comment: ${response.status} ${text}`)
  }
}

/**
 * Post a reaction on a comment to acknowledge processing.
 */
export async function postCommentReaction(
  owner: string,
  repo: string,
  commentId: number,
  reaction: string,
  token: string
): Promise<void> {
  const url = `https://api.github.com/repos/${owner}/${repo}/issues/comments/${commentId}/reactions`
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "article-checker-worker",
    },
    body: JSON.stringify({ content: reaction }),
  })

  if (!response.ok) {
    console.warn(`Failed to post reaction: ${response.status}`)
  }
}
