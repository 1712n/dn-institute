import type { Env, WebhookPayload, DiffFile } from "./types";

/**
 * Verify GitHub webhook HMAC-SHA256 signature using timing-safe comparison.
 */
export async function verifySignature(
  body: string,
  signature: string | null,
  secret: string
): Promise<boolean> {
  if (!signature || !signature.startsWith("sha256=")) return false;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signed = await crypto.subtle.sign("HMAC", key, encoder.encode(body));
  const expectedBytes = new Uint8Array(signed);

  // Parse the hex signature from GitHub
  const sigHex = signature.slice("sha256=".length);
  if (sigHex.length !== expectedBytes.length * 2) return false;
  // Validate hex string contains only valid hex characters
  if (!/^[0-9a-f]+$/i.test(sigHex)) return false;

  const actualBytes = new Uint8Array(expectedBytes.length);
  for (let i = 0; i < actualBytes.length; i++) {
    actualBytes[i] = parseInt(sigHex.slice(i * 2, i * 2 + 2), 16);
  }

  // Constant-time comparison to prevent timing attacks
  return timingSafeEqual(expectedBytes, actualBytes);
}

/**
 * Constant-time comparison of two byte arrays.
 * Prevents timing-based side-channel attacks on signature verification.
 */
function timingSafeEqual(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= (a[i] ?? 0) ^ (b[i] ?? 0);
  }
  return result === 0;
}

/**
 * Check if the commenter is in the allowed reviewers list.
 */
export function isAllowedReviewer(
  actor: string,
  reviewersJson: string
): boolean {
  try {
    const reviewers: string[] = JSON.parse(reviewersJson);
    return reviewers.includes(actor);
  } catch {
    return false;
  }
}

/**
 * Fetch the PR diff from GitHub.
 */
export async function fetchPrDiff(
  diffUrl: string,
  token: string
): Promise<string> {
  const resp = await fetch(diffUrl, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "articlecheck-worker",
    },
  });
  if (!resp.ok) {
    throw new Error(`Failed to fetch diff: ${resp.status} ${resp.statusText}`);
  }
  return resp.text();
}

/**
 * Parse a unified diff into structured file objects.
 * Matches the Python parse_diff behavior: splits on "diff --git " and "@@"
 * segments, returning header + body pairs for each hunk.
 */
export function parseDiff(diff: string): DiffFile[] {
  const rawFiles = diff.split("diff --git ");
  rawFiles.shift(); // remove empty first element

  return rawFiles.map((raw) => {
    const segments = raw.split("@@");
    const header = segments.shift() ?? "";

    // Build body segments as pairs: [range_info, content] matching Python behavior
    const bodySegments: Array<{ header: string; body: string }> = [];
    for (let i = 0; i < segments.length; i += 2) {
      if (segments[i + 1] !== undefined) {
        bodySegments.push({
          header: segments[i]!,
          body: segments[i + 1]!,
        });
      }
    }
    return { header, bodySegments };
  });
}

/**
 * Extract article text from parsed diff files.
 * Matches Python behavior: first file, first hunk only.
 *   text = remove_plus(diff[0]['header'] + diff[0]['body'][0]['body'])
 */
export function extractArticleText(files: DiffFile[]): string | null {
  if (files.length === 0) return null;
  const file = files[0]!;
  const firstBody = file.bodySegments[0]?.body ?? "";
  return removePlus(file.header + firstBody);
}

/**
 * Strip leading '+' from diff lines (added lines).
 */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.startsWith("+") ? line.slice(1) : line))
    .join("\n");
}

/**
 * Post a comment on a GitHub PR.
 */
export async function postPrComment(
  repo: string,
  prNumber: number,
  body: string,
  token: string
): Promise<void> {
  const url = `https://api.github.com/repos/${repo}/issues/${prNumber}/comments`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "articlecheck-worker",
    },
    body: JSON.stringify({ body }),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Failed to post comment: ${resp.status} ${text}`);
  }
}

/**
 * Check if the bot has already posted a review comment on this PR.
 * Looks for the HTML marker comment.
 */
export async function hasExistingReview(
  repo: string,
  prNumber: number,
  token: string
): Promise<boolean> {
  const url = `https://api.github.com/repos/${repo}/issues/${prNumber}/comments?per_page=100`;
  const resp = await fetch(url, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3+json",
      "User-Agent": "articlecheck-worker",
    },
  });
  if (!resp.ok) return false;

  const comments = (await resp.json()) as Array<{ body: string }>;
  return comments.some((c) => c.body.includes("<!-- articlecheck-worker -->"));
}
