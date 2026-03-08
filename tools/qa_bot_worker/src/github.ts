import type { DiffFile } from "./types";

/**
 * Verify GitHub webhook signature (HMAC-SHA256).
 * @see https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
 */
export async function verifyGitHubWebhook(
  payload: string,
  signature: string | null,
  secret: string
): Promise<boolean> {
  if (!signature) return false;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
  const digest = "sha256=" + arrayBufferToHex(sig);

  return secureCompare(digest, signature);
}

function arrayBufferToHex(buffer: ArrayBuffer): string {
  return [...new Uint8Array(buffer)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/** Constant-time string comparison to prevent timing attacks */
function secureCompare(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  const encoder = new TextEncoder();
  const aBuf = encoder.encode(a);
  const bBuf = encoder.encode(b);
  let result = 0;
  for (let i = 0; i < aBuf.length; i++) {
    result |= aBuf[i] ^ bBuf[i];
  }
  return result === 0;
}

/**
 * Fetch the diff text for a pull request.
 */
export async function fetchDiff(
  diffUrl: string,
  token: string
): Promise<string> {
  const response = await fetch(diffUrl, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "dn-institute-qa-bot",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch diff: HTTP ${response.status}`);
  }

  return response.text();
}

/**
 * Parse a unified diff and extract added lines per file.
 * Returns filename and cleaned additions (with leading '+' stripped).
 */
export function parseDiff(rawDiff: string): DiffFile[] {
  const files: DiffFile[] = [];
  const fileSections = rawDiff.split("diff --git ");

  for (const section of fileSections) {
    if (!section.trim()) continue;

    // Extract filename from "a/path b/path"
    const fileMatch = section.match(/^a\/(.+?) b\//);
    const filename = fileMatch ? fileMatch[1] : "unknown";

    // Extract added lines (lines starting with + but not +++ header)
    const lines = section.split("\n");
    const additions: string[] = [];
    for (const line of lines) {
      if (line.startsWith("+") && !line.startsWith("+++")) {
        additions.push(line.substring(1)); // strip leading '+'
      }
    }

    if (additions.length > 0) {
      files.push({ filename, additions: additions.join("\n") });
    }
  }

  return files;
}

/**
 * Post a comment on a GitHub pull request / issue.
 */
export async function postComment(
  repoFullName: string,
  issueNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `https://api.github.com/repos/${repoFullName}/issues/${issueNumber}/comments`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "dn-institute-qa-bot",
    },
    body: JSON.stringify({ body }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Failed to post comment: HTTP ${response.status} — ${text}`);
  }
}

/**
 * Get the diff URL for a pull request given its API URL.
 */
export async function getPrDiffUrl(
  prApiUrl: string,
  token: string
): Promise<{ diffUrl: string; number: number; repoFullName: string }> {
  const response = await fetch(prApiUrl, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "dn-institute-qa-bot",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch PR info: HTTP ${response.status}`);
  }

  const data = (await response.json()) as {
    diff_url: string;
    number: number;
    base: { repo: { full_name: string } };
  };

  return {
    diffUrl: data.diff_url,
    number: data.number,
    repoFullName: data.base.repo.full_name,
  };
}
