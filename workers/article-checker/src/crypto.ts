/**
 * Cryptographic utilities for verifying GitHub webhook signatures.
 * Uses the Web Crypto API available in Cloudflare Workers.
 */

/**
 * Verify that a GitHub webhook payload signature is valid.
 * GitHub sends an HMAC-SHA256 signature in the `X-Hub-Signature-256` header.
 *
 * @param payload - The raw request body as a string
 * @param signature - The signature from the X-Hub-Signature-256 header
 * @param secret - The webhook secret configured in GitHub
 * @returns true if the signature is valid
 */
export async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  if (!signature || !signature.startsWith("sha256=")) {
    return false;
  }

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const signatureBuffer = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode(payload)
  );

  const expectedSignature =
    "sha256=" +
    Array.from(new Uint8Array(signatureBuffer))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

  // Constant-time comparison to prevent timing attacks
  if (expectedSignature.length !== signature.length) {
    return false;
  }

  let mismatch = 0;
  for (let i = 0; i < expectedSignature.length; i++) {
    mismatch |= expectedSignature.charCodeAt(i) ^ signature.charCodeAt(i);
  }

  return mismatch === 0;
}
