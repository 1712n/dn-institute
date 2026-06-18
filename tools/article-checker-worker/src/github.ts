import type { DiffFile, DiffSegment } from "./types"

/**
 * Verify the GitHub webhook signature (HMAC SHA-256).
 * Returns true if valid, false otherwise.
 */
export async function verifyWebhookSignature(
  payload: string,
  signature: string | null,
  secret: string
): Promise<boolean> {
  if (!signature || !signature.startsWith("sha256=")) {
    return false
  }

  const encoder = new TextEncoder()
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  )
  const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(payload))
  const expectedHex = Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")

  const receivedHex = signature.slice("sha256=".length)

  // Constant-time comparison
  if (expectedHex.length !== receivedHex.length) {
    return false
  }
  let mismatch = 0
  for (let i = 0; i < expectedHex.length; i++) {
    mismatch |= expectedHex.charCodeAt(i) ^ receivedHex.charCodeAt(i)
  }
  return mismatch === 0
}

/**
 * Fetch the diff content for a pull request.
 */
export async function fetchPRDiff(
  owner: string,
  repo: string,
  prNumber: number,
  githubToken: string
): Promise<string> {
  const url = `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}`
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${githubToken}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "article-checker-worker",
    },
  })

  if (!response.ok) {
    throw new Error(
      `Failed to fetch PR diff: ${response.status} ${response.statusText}`
    )
  }

  return response.text()
}

/**
 * Parse a unified diff string into structured file objects.
 * Mirrors the Python parse_diff function.
 */
export function parseDiff(diff: string): DiffFile[] {
  const rawFiles = diff.split("diff --git ")
  // Remove first element (empty string before first diff)
  rawFiles.shift()

  const files: DiffFile[] = []

  for (const rawFile of rawFiles) {
    const rawSegments = rawFile.split("@@")
    // First element is the file header
    const fileHeader = rawSegments.shift() || ""

    const segments: DiffSegment[] = []
    for (let i = 0; i < rawSegments.length; i += 2) {
      if (i + 1 < rawSegments.length) {
        segments.push({
          header: rawSegments[i],
          body: rawSegments[i + 1],
        })
      }
    }

    files.push({
      header: fileHeader,
      body: segments,
    })
  }

  return files
}

/**
 * Remove leading '+' from diff lines (added lines in unified diff).
 * Mirrors the Python remove_plus function.
 */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.startsWith("+") ? line.slice(1) : line))
    .join("\n")
}

/**
 * Post a comment on a GitHub pull request.
 */
export async function postPRComment(
  owner: string,
  repo: string,
  prNumber: number,
  body: string,
  githubToken: string
): Promise<void> {
  const url = `https://api.github.com/repos/${owner}/${repo}/issues/${prNumber}/comments`
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${githubToken}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "article-checker-worker",
    },
    body: JSON.stringify({ body }),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(
      `Failed to post PR comment: ${response.status} ${response.statusText} - ${text}`
    )
  }
}
