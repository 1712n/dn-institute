/**
 * github.ts — GitHub API helpers.
 *
 * Handles:
 *  - Fetching a PR diff via the GitHub API
 *  - Parsing that diff into structured file segments (port of parse_diff from
 *    tools/python_modules/git.py)
 *  - Posting a comment on a PR
 *  - Stripping leading '+' characters from diff lines (port of remove_plus from
 *    tools/python_modules/llm_utils.py)
 */

export interface DiffSegment {
  header: string;
  body: string;
}

export interface DiffFile {
  header: string;
  body: DiffSegment[];
}

// ---------------------------------------------------------------------------
// fetch PR diff
// ---------------------------------------------------------------------------

/**
 * Fetch the raw unified diff for a pull request.
 *
 * GitHub returns the diff when you request the PR URL with the
 * `application/vnd.github.v3.diff` accept header.
 *
 * @param prApiUrl  Full GitHub API URL for the PR, e.g.
 *                  https://api.github.com/repos/owner/repo/pulls/123
 * @param token     GitHub personal access token (or Actions token).
 */
export async function getPrDiff(prApiUrl: string, token: string): Promise<string> {
  const response = await fetch(prApiUrl, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "dn-article-checker-worker/1.0",
    },
  });

  if (!response.ok) {
    throw new Error(
      `GitHub diff fetch failed: ${response.status} ${response.statusText} for ${prApiUrl}`
    );
  }

  return response.text();
}

// ---------------------------------------------------------------------------
// parseDiff — port of tools/python_modules/git.py parse_diff()
// ---------------------------------------------------------------------------

/**
 * Parse a raw git unified diff into an array of file objects.
 *
 * Each file object has a `header` (the lines before the first @@) and a
 * `body` array of `{ header, body }` segment pairs that correspond to the @@
 * hunks in the diff.
 *
 * This is a direct port of the Python `parse_diff` function.
 */
export function parseDiff(diff: string): DiffFile[] {
  // Split into per-file sections (the first element before the first
  // "diff --git" is always empty and gets discarded).
  const rawFiles = diff.split("diff --git ");
  rawFiles.shift(); // remove the leading empty string

  const files: DiffFile[] = [];

  for (const rawFile of rawFiles) {
    // Split each file blob into alternating header/body segments separated by @@
    const rawSegments = rawFile.split("@@");

    // The first element is the file header (the a/b path lines, index line, etc.)
    const fileHeader = rawSegments.shift() ?? "";

    // Every pair of remaining elements forms one hunk:
    //   rawSegments[0] = @@ -x,y +x,y @@ (the hunk header)
    //   rawSegments[1] = the actual diff lines
    const segments: DiffSegment[] = [];
    for (let i = 0; i < rawSegments.length; i += 2) {
      const segHeader = rawSegments[i] ?? "";
      const segBody = rawSegments[i + 1] ?? "";
      segments.push({ header: segHeader, body: segBody });
    }

    files.push({ header: fileHeader, body: segments });
  }

  return files;
}

// ---------------------------------------------------------------------------
// extractArticleText — combines file header + first hunk body, then strips '+'
// ---------------------------------------------------------------------------

/**
 * Pull the article text out of the first file's first hunk.
 *
 * This mirrors the logic in article_checker_claude.py:
 *   text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
 */
export function extractArticleText(files: DiffFile[]): string {
  const firstFile = files[0];
  if (!firstFile) {
    throw new Error("parseDiff returned no files — is the PR empty?");
  }

  const firstBody = firstFile.body[0];
  const raw = firstFile.header + (firstBody ? firstBody.body : "");
  return removePlus(raw);
}

// ---------------------------------------------------------------------------
// removePlus — port of tools/python_modules/llm_utils.py remove_plus()
// ---------------------------------------------------------------------------

/**
 * Strip the leading '+' from each line of a diff body so that Claude sees
 * clean article text rather than raw diff markers.
 */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => line.replace(/^\+/, ""))
    .join("\n");
}

// ---------------------------------------------------------------------------
// postComment — post a markdown comment on a PR
// ---------------------------------------------------------------------------

/**
 * Post a comment on a GitHub pull request (or issue — they share the API).
 *
 * @param commentsUrl  The `comments_url` field from the webhook payload, e.g.
 *                     https://api.github.com/repos/owner/repo/issues/123/comments
 * @param body         Markdown body for the comment.
 * @param token        GitHub token.
 */
export async function postComment(
  commentsUrl: string,
  body: string,
  token: string
): Promise<void> {
  const response = await fetch(commentsUrl, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "dn-article-checker-worker/1.0",
    },
    body: JSON.stringify({ body }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `Failed to post GitHub comment: ${response.status} ${response.statusText}\n${text}`
    );
  }
}
