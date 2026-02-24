/**
 * GitHub API helpers — fetch PR diffs, parse unified diffs, post comments.
 */

export interface DiffFile {
  filename: string;
  content: string;
}

/**
 * Fetch the raw unified diff for a pull request.
 */
export async function fetchPRDiff(
  prApiUrl: string,
  token: string
): Promise<string> {
  const res = await fetch(prApiUrl, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "dn-institute-qa-bot",
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch PR diff: ${res.status} ${res.statusText}`);
  }
  return res.text();
}

/**
 * Parse a unified diff into per-file additions.
 * Only keeps added lines (starting with "+") from Markdown content files.
 * Strips the leading "+" and frontmatter/header prefixes are preserved.
 */
export function parseDiff(raw: string): DiffFile[] {
  const files: DiffFile[] = [];
  const fileSections = raw.split(/^diff --git /m).filter(Boolean);

  for (const section of fileSections) {
    // Extract filename from "a/path b/path" line
    const headerMatch = section.match(/^a\/(.+?) b\/(.+)/m);
    if (!headerMatch) continue;

    const filename = headerMatch[2];

    // Only process Markdown files in content/ directory (attack wiki articles)
    if (!filename.startsWith("content/") || !filename.endsWith(".md")) {
      continue;
    }

    // Collect added lines (lines starting with "+", but not "+++ b/...")
    const lines = section.split("\n");
    const addedLines: string[] = [];

    for (const line of lines) {
      if (line.startsWith("+++")) continue; // skip diff header
      if (line.startsWith("+")) {
        addedLines.push(line.slice(1)); // strip leading "+"
      }
    }

    if (addedLines.length > 0) {
      files.push({ filename, content: addedLines.join("\n") });
    }
  }

  return files;
}

/**
 * Post a comment on a pull request via the GitHub Issues API.
 */
export async function postComment(
  repoFullName: string,
  prNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `https://api.github.com/repos/${repoFullName}/issues/${prNumber}/comments`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "dn-institute-qa-bot",
    },
    body: JSON.stringify({ body }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to post comment: ${res.status} ${text}`);
  }
}
