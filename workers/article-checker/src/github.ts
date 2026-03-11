// 🌰 GitHub API client for PR interactions 🌰

/**
 * 🌰 Fetch the diff for a pull request.
 * Uses the diff_url from the webhook payload.
 */
export async function getPullRequestDiff(
  owner: string,
  repo: string,
  prNumber: number,
  token: string,
): Promise<string> {
  const url = `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}`;

  const response = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "article-checker-worker",
    },
  });

  if (!response.ok) {
    throw new Error(
      `🌰 Failed to fetch PR diff: ${response.status} ${response.statusText}`,
    );
  }

  return response.text();
}

/**
 * 🌰 Post a comment on a pull request.
 */
export async function createPRComment(
  owner: string,
  repo: string,
  prNumber: number,
  body: string,
  token: string,
): Promise<void> {
  const url = `https://api.github.com/repos/${owner}/${repo}/issues/${prNumber}/comments`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "User-Agent": "article-checker-worker",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ body }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `🌰 Failed to post PR comment: ${response.status} ${errorText}`,
    );
  }

  console.log("🌰 Successfully posted review comment on PR");
}

/**
 * 🌰 Post a reaction on the trigger comment to acknowledge receipt.
 */
export async function addCommentReaction(
  owner: string,
  repo: string,
  commentId: number,
  reaction: string,
  token: string,
): Promise<void> {
  const url = `https://api.github.com/repos/${owner}/${repo}/issues/comments/${commentId}/reactions`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "article-checker-worker",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content: reaction }),
  });

  if (!response.ok) {
    // 🌰 Non-critical: don't throw, just log
    console.warn(`🌰 Failed to add reaction: ${response.status}`);
  }
}

/**
 * 🌰 Fetch all changed files in a PR with pagination support.
 * Returns the list of filenames that were modified.
 */
export async function getPRChangedFiles(
  owner: string,
  repo: string,
  prNumber: number,
  token: string,
): Promise<string[]> {
  const files: string[] = [];
  let page = 1;
  const perPage = 100;

  // 🌰 Paginate through all changed files
  while (true) {
    const url = `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/files?per_page=${perPage}&page=${page}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `token ${token}`,
        Accept: "application/vnd.github.v3+json",
        "User-Agent": "article-checker-worker",
      },
    });

    if (!response.ok) break;

    const pageFiles: Array<{ filename: string }> = await response.json();
    if (pageFiles.length === 0) break;

    files.push(...pageFiles.map((f) => f.filename));
    if (pageFiles.length < perPage) break;
    page++;
  }

  return files;
}
