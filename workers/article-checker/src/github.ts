/**
 * GitHub API integration module.
 * Handles fetching PR diffs and posting comments.
 */

import type { DiffFile, DiffSegment } from "./types";

const GITHUB_API_BASE = "https://api.github.com";

/**
 * Fetch the diff for a pull request.
 *
 * @param repo - The full repository name (owner/repo)
 * @param prNumber - The PR number
 * @param token - GitHub API token
 * @returns The raw diff text
 */
export async function fetchPRDiff(
  repo: string,
  prNumber: number,
  token: string
): Promise<string> {
  const url = `${GITHUB_API_BASE}/repos/${repo}/pulls/${prNumber}`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "dn-institute-article-checker-worker",
    },
  });

  if (!response.ok) {
    throw new Error(
      `Failed to fetch PR diff: ${response.status} ${response.statusText}`
    );
  }

  return response.text();
}

/**
 * Parse a unified diff string into structured file objects.
 * This mirrors the Python parse_diff() function.
 *
 * @param diff - The raw unified diff text
 * @returns Array of parsed diff files
 */
export function parseDiff(diff: string): DiffFile[] {
  const rawFiles = diff.split("diff --git ");
  // Remove the first empty element
  rawFiles.shift();

  const files: DiffFile[] = [];

  for (const rawFile of rawFiles) {
    const rawSegments = rawFile.split("@@");
    // First element is the file header
    const fileHeader = rawSegments.shift() || "";

    const segments: DiffSegment[] = [];
    for (let i = 0; i < rawSegments.length; i += 2) {
      if (i + 1 < rawSegments.length) {
        segments.push({
          header: rawSegments[i],
          body: rawSegments[i + 1],
        });
      }
    }

    files.push({
      header: fileHeader,
      body: segments,
    });
  }

  return files;
}

/**
 * Remove leading '+' characters from diff lines.
 * This mirrors the Python remove_plus() function.
 *
 * @param text - The diff text with '+' prefixes
 * @returns Text with '+' prefixes removed
 */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.startsWith("+") ? line.slice(1) : line))
    .join("\n");
}

/**
 * Post a comment on a GitHub pull request.
 *
 * @param repo - The full repository name (owner/repo)
 * @param prNumber - The PR number
 * @param body - The comment body (Markdown)
 * @param token - GitHub API token
 */
export async function postPRComment(
  repo: string,
  prNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `${GITHUB_API_BASE}/repos/${repo}/issues/${prNumber}/comments`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "dn-institute-article-checker-worker",
    },
    body: JSON.stringify({ body }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `Failed to post PR comment: ${response.status} ${response.statusText} - ${errorBody}`
    );
  }
}

/**
 * Add a reaction to a comment (e.g., "eyes" to acknowledge command receipt).
 *
 * @param repo - The full repository name (owner/repo)
 * @param commentId - The comment ID to react to
 * @param reaction - The reaction type (e.g., "eyes", "rocket", "+1")
 * @param token - GitHub API token
 */
export async function addCommentReaction(
  repo: string,
  commentId: number,
  reaction: string,
  token: string
): Promise<void> {
  const url = `${GITHUB_API_BASE}/repos/${repo}/issues/comments/${commentId}/reactions`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github.squirrel-girl-preview+json",
      "Content-Type": "application/json",
      "User-Agent": "dn-institute-article-checker-worker",
    },
    body: JSON.stringify({ content: reaction }),
  });

  if (!response.ok) {
    console.warn(
      `Failed to add reaction: ${response.status} ${response.statusText}`
    );
  }
}
