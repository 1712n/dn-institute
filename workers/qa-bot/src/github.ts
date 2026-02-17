/**
 * GitHub API helpers — minimal, no external dependencies.
 */

const GITHUB_API = "https://api.github.com";

interface GHHeaders {
  Authorization: string;
  Accept: string;
  "User-Agent": string;
}

function headers(token: string): GHHeaders {
  return {
    Authorization: `token ${token}`,
    Accept: "application/vnd.github.v3+json",
    "User-Agent": "dn-institute-qa-bot/1.0",
  };
}

/** Fetch PR metadata (returns owner, repo, number, diff_url, etc.) */
export async function getPullRequest(prApiUrl: string, token: string) {
  const res = await fetch(prApiUrl, { headers: headers(token) });
  if (!res.ok) throw new Error(`GitHub PR fetch failed: ${res.status} ${await res.text()}`);
  return res.json() as Promise<any>;
}

/** Fetch the unified diff for a PR */
export async function getPRDiff(prApiUrl: string, token: string): Promise<string> {
  const res = await fetch(prApiUrl, {
    headers: {
      ...headers(token),
      Accept: "application/vnd.github.v3.diff",
    },
  });
  if (!res.ok) throw new Error(`GitHub diff fetch failed: ${res.status}`);
  return res.text();
}

/** Post a comment on the PR's issue thread */
export async function postComment(prApiUrl: string, token: string, body: string): Promise<void> {
  // PR API URL: /repos/{owner}/{repo}/pulls/{number}
  // Issue comments URL: /repos/{owner}/{repo}/issues/{number}/comments
  const issueCommentsUrl = prApiUrl.replace("/pulls/", "/issues/") + "/comments";
  const res = await fetch(issueCommentsUrl, {
    method: "POST",
    headers: {
      ...headers(token),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ body }),
  });
  if (!res.ok) throw new Error(`GitHub comment post failed: ${res.status} ${await res.text()}`);
}
