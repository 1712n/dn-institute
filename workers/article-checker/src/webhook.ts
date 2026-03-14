/**
 * webhook.ts — GitHub webhook handling.
 *
 * Responsibilities:
 *  1. Verify the X-Hub-Signature-256 HMAC signature (guards against spoofed requests)
 *  2. Parse issue_comment webhook events
 *  3. Gate on `/articlecheck` in the comment body
 *  4. Gate on commenter being in WIKI_REVIEWERS
 *
 * The actual fact-checking is kicked off asynchronously via ctx.waitUntil()
 * in index.ts — this module only decides whether to proceed and returns the
 * structured data the checker needs.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Minimal subset of the GitHub issue_comment webhook payload we need. */
export interface IssueCommentPayload {
  action: string;
  issue: {
    number: number;
    title: string;
    pull_request?: {
      url: string; // API URL of the PR, e.g. https://api.github.com/repos/…/pulls/123
    };
    comments_url: string;
  };
  comment: {
    body: string;
    user: {
      login: string;
    };
  };
  repository: {
    full_name: string;
  };
}

export interface WebhookCheckResult {
  /** Whether the worker should proceed with fact-checking */
  proceed: boolean;
  /** Human-readable reason when proceed === false (for debug logs) */
  reason?: string;
  payload?: IssueCommentPayload;
}

// ---------------------------------------------------------------------------
// Signature verification
// ---------------------------------------------------------------------------

/**
 * Verify the X-Hub-Signature-256 header using HMAC-SHA256.
 *
 * Uses the Web Crypto API (available in Cloudflare Workers) rather than Node's
 * crypto module.
 *
 * @param body          Raw request body bytes
 * @param signature     Value of X-Hub-Signature-256 header (e.g. "sha256=abc…")
 * @param secret        Webhook secret configured on the GitHub repo
 */
export async function verifySignature(
  body: ArrayBuffer,
  signature: string,
  secret: string
): Promise<boolean> {
  if (!signature.startsWith("sha256=")) return false;

  const expectedHex = signature.slice(7); // strip "sha256="

  const encoder = new TextEncoder();
  const keyData = encoder.encode(secret);

  const key = await crypto.subtle.importKey(
    "raw",
    keyData,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const mac = await crypto.subtle.sign("HMAC", key, body);

  // Convert the HMAC bytes to a hex string
  const actualHex = Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  // Constant-time comparison to prevent timing attacks
  return timingSafeEqual(actualHex, expectedHex);
}

/** Constant-time string comparison (both must be same length hex strings). */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

// ---------------------------------------------------------------------------
// Authorisation check
// ---------------------------------------------------------------------------

/**
 * Check whether `username` is in the comma-separated WIKI_REVIEWERS list.
 *
 * Case-insensitive to avoid foot-guns with GitHub username casing.
 */
export function isAuthorised(username: string, wikiReviewers: string): boolean {
  const allowed = wikiReviewers
    .split(",")
    .map((u) => u.trim().toLowerCase())
    .filter(Boolean);
  return allowed.includes(username.toLowerCase());
}

// ---------------------------------------------------------------------------
// processWebhook — main entry point called from index.ts
// ---------------------------------------------------------------------------

/**
 * Process an incoming GitHub webhook request.
 *
 * Returns a WebhookCheckResult indicating whether the fact-checker should run
 * and (if so) the structured payload data it needs.
 *
 * @param request        The incoming HTTP request (body will be read once)
 * @param webhookSecret  WEBHOOK_SECRET from wrangler env
 * @param wikiReviewers  WIKI_REVIEWERS from wrangler env (comma-separated)
 */
export async function processWebhook(
  request: Request,
  webhookSecret: string,
  wikiReviewers: string
): Promise<{ result: WebhookCheckResult; bodyText: string }> {
  // Read the body once; we need the raw bytes for signature verification AND
  // the text for JSON parsing.
  const bodyBytes = await request.arrayBuffer();
  const bodyText = new TextDecoder().decode(bodyBytes);

  // 1. Verify signature
  const signature = request.headers.get("X-Hub-Signature-256") ?? "";
  const valid = await verifySignature(bodyBytes, signature, webhookSecret);
  if (!valid) {
    return {
      result: { proceed: false, reason: "Invalid webhook signature" },
      bodyText,
    };
  }

  // 2. Only handle issue_comment events
  const eventType = request.headers.get("X-GitHub-Event") ?? "";
  if (eventType !== "issue_comment") {
    return {
      result: {
        proceed: false,
        reason: `Ignored event type: ${eventType}`,
      },
      bodyText,
    };
  }

  // 3. Parse payload
  let payload: IssueCommentPayload;
  try {
    payload = JSON.parse(bodyText) as IssueCommentPayload;
  } catch {
    return {
      result: { proceed: false, reason: "Failed to parse JSON body" },
      bodyText,
    };
  }

  // 4. Only handle "created" actions
  if (payload.action !== "created") {
    return {
      result: { proceed: false, reason: `Ignored action: ${payload.action}` },
      bodyText,
    };
  }

  // 5. Only handle comments on pull requests (not plain issues)
  if (!payload.issue.pull_request) {
    return {
      result: { proceed: false, reason: "Comment is not on a pull request" },
      bodyText,
    };
  }

  // 6. Must contain /articlecheck
  if (!payload.comment.body.includes("/articlecheck")) {
    return {
      result: {
        proceed: false,
        reason: "Comment does not contain /articlecheck",
      },
      bodyText,
    };
  }

  // 7. Must be from an authorised reviewer
  const commenter = payload.comment.user.login;
  if (!isAuthorised(commenter, wikiReviewers)) {
    return {
      result: {
        proceed: false,
        reason: `${commenter} is not in WIKI_REVIEWERS`,
      },
      bodyText,
    };
  }

  return {
    result: { proceed: true, payload },
    bodyText,
  };
}
