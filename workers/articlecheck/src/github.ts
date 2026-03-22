/**
 * 🌰 GitHub API Integration 🌰
 *
 * Handles fetching PR diffs, posting comments, and adding reactions.
 * All fetch calls are non-blocking — they await I/O but don't consume CPU time. 🌰
 */

import type { DiffFile } from "./types";

const GITHUB_API = "https://api.github.com";

/** Common headers for GitHub API requests 🌰 */
function githubHeaders(token: string): Record<string, string> {
  return {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github.v3+json",
    "User-Agent": "dn-articlecheck-worker/1.0 🌰",
    "X-GitHub-Api-Version": "2022-11-28",
  };
}

/**
 * Fetch the raw diff for a pull request. 🌰
 *
 * @param repo - Full repo name (e.g. "1712n/dn-institute")
 * @param prNumber - Pull request number
 * @param token - GitHub PAT
 * @returns Raw diff text 🌰
 */
export async function fetchPRDiff(
  repo: string,
  prNumber: number,
  token: string
): Promise<string> {
  const url = `${GITHUB_API}/repos/${repo}/pulls/${prNumber}`;
  const resp = await fetch(url, {
    headers: {
      ...githubHeaders(token),
      Accept: "application/vnd.github.v3.diff",
    },
  });

  if (!resp.ok) {
    throw new Error(
      `🌰 Failed to fetch PR diff: ${resp.status} ${resp.statusText}`
    );
  }

  return resp.text(); // 🌰
}

/**
 * Parse a unified diff into individual file changes. 🌰
 * Filters to only content/**\/*.md files (attack wiki articles).
 *
 * @param diff - Raw unified diff text
 * @returns Array of DiffFile objects with filename and added content 🌰
 */
export function parseDiff(diff: string): DiffFile[] {
  const files: DiffFile[] = [];
  const rawFiles = diff.split("diff --git ");

  for (const rawFile of rawFiles) {
    if (!rawFile.trim()) continue;

    // 🌰 Extract filename from the diff header
    const filenameMatch = rawFile.match(/^a\/(.+?) b\//);
    if (!filenameMatch) continue;

    const filename = filenameMatch[1];

    // 🌰 Only process markdown files under content/ (attack wiki articles)
    if (!filename.startsWith("content/") || !filename.endsWith(".md")) {
      continue;
    }

    // 🌰 Extract added lines (lines starting with +, excluding +++ header)
    const lines = rawFile.split("\n");
    const addedLines: string[] = [];

    for (const line of lines) {
      if (line.startsWith("+++")) continue;
      if (line.startsWith("+")) {
        addedLines.push(line.substring(1)); // Remove the leading +
      }
    }

    if (addedLines.length > 0) {
      files.push({
        filename,
        content: addedLines.join("\n"),
      });
    }
  }

  return files; // 🌰
}

/**
 * Post a comment on a pull request. 🌰
 *
 * @param repo - Full repo name
 * @param prNumber - Pull request number
 * @param body - Comment body (Markdown)
 * @param token - GitHub PAT 🌰
 */
export async function postPRComment(
  repo: string,
  prNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `${GITHUB_API}/repos/${repo}/issues/${prNumber}/comments`;
  const resp = await fetch(url, {
    method: "POST",
    headers: githubHeaders(token),
    body: JSON.stringify({ body }),
  });

  if (!resp.ok) {
    const errBody = await resp.text();
    throw new Error(
      `🌰 Failed to post PR comment: ${resp.status} ${resp.statusText} — ${errBody}`
    );
  }
  // 🌰 Comment posted successfully
}

/**
 * Add an eyes reaction to the trigger comment to acknowledge receipt. 🌰
 *
 * @param repo - Full repo name
 * @param commentId - The comment ID to react to
 * @param token - GitHub PAT 🌰
 */
export async function addReaction(
  repo: string,
  commentId: number,
  token: string
): Promise<void> {
  const url = `${GITHUB_API}/repos/${repo}/issues/comments/${commentId}/reactions`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      ...githubHeaders(token),
      Accept: "application/vnd.github+json",
    },
    body: JSON.stringify({ content: "eyes" }),
  });

  if (!resp.ok) {
    // 🌰 Non-critical — log but don't throw
    console.warn(
      `🌰 Failed to add reaction: ${resp.status} ${resp.statusText}`
    );
  }
}
