import { verifyHmacSha256HexSignature } from "../crypto";

export type GitHubWebhookHeaders = {
  event: string | null;
  deliveryId: string | null;
  signature256: string | null;
};

export function readGitHubWebhookHeaders(headers: Headers): GitHubWebhookHeaders {
  return {
    event: headers.get("X-GitHub-Event"),
    deliveryId: headers.get("X-GitHub-Delivery"),
    signature256: headers.get("X-Hub-Signature-256")
  };
}

export async function verifyGitHubWebhookSignature(opts: {
  headers: GitHubWebhookHeaders;
  secret: string | undefined;
  rawBody: ArrayBuffer;
}): Promise<{ ok: true } | { ok: false; reason: string }> {
  if (!opts.secret) return { ok: false, reason: "missing_webhook_secret" };
  const sig = opts.headers.signature256;
  if (!sig || !sig.startsWith("sha256=")) return { ok: false, reason: "missing_signature" };
  const expected = sig.slice("sha256=".length);
  if (!expected) return { ok: false, reason: "missing_signature_digest" };
  const ok = await verifyHmacSha256HexSignature({
    secret: opts.secret,
    payload: opts.rawBody,
    expectedHexDigest: expected
  });
  return ok ? { ok: true } : { ok: false, reason: "bad_signature" };
}

