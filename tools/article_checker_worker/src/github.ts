const GH_API = "https://api.github.com";

export async function fetchPullRequestDiff(
  token: string,
  repo: string,
  prNumber: number,
): Promise<string> {
  const r = await fetch(`${GH_API}/repos/${repo}/pulls/${prNumber}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "dn-article-checker-worker/0.1",
    },
  });
  if (!r.ok) throw new Error(`GitHub diff fetch failed: ${r.status} ${await r.text()}`);
  return await r.text();
}

export async function postPullRequestComment(
  token: string,
  repo: string,
  prNumber: number,
  body: string,
): Promise<void> {
  const r = await fetch(`${GH_API}/repos/${repo}/issues/${prNumber}/comments`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "dn-article-checker-worker/0.1",
    },
    body: JSON.stringify({ body }),
  });
  if (!r.ok) throw new Error(`GitHub comment post failed: ${r.status} ${await r.text()}`);
}
