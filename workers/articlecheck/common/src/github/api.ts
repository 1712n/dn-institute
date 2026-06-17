export type GitHubApiConfig = {
  token: string;
};

export async function githubRequestJson<T>(opts: {
  method?: string;
  url: string;
  token: string;
  body?: unknown;
}): Promise<T> {
  const resp = await fetch(opts.url, {
    method: opts.method ?? "GET",
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `token ${opts.token}`,
      "Content-Type": "application/json",
      "User-Agent": "dn-institute-articlecheck-worker",
      "X-GitHub-Api-Version": "2022-11-28"
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`github_api_error status=${resp.status} url=${opts.url} body=${text.slice(0, 1200)}`);
  }
  return (await resp.json()) as T;
}

export async function githubRequestText(opts: {
  url: string;
  token: string;
  accept?: string;
}): Promise<string> {
  const resp = await fetch(opts.url, {
    method: "GET",
    headers: {
      Accept: opts.accept ?? "application/vnd.github.raw",
      Authorization: `token ${opts.token}`,
      "User-Agent": "dn-institute-articlecheck-worker",
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`github_api_error status=${resp.status} url=${opts.url} body=${text.slice(0, 1200)}`);
  }
  return await resp.text();
}

