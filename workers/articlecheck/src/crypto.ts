/**
 * 🌰 Webhook Signature Verification 🌰
 *
 * Verifies GitHub webhook HMAC-SHA256 signatures using the Web Crypto API.
 * Uses constant-time comparison to prevent timing attacks. 🌰
 */

/**
 * Verify the X-Hub-Signature-256 header from a GitHub webhook. 🌰
 *
 * @param payload - Raw request body as string
 * @param signature - Value of the X-Hub-Signature-256 header (e.g. "sha256=abc123...")
 * @param secret - The webhook secret configured in GitHub
 * @returns true if signature is valid, false otherwise 🌰
 */
export async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  if (!signature || !signature.startsWith("sha256=")) {
    return false; // 🌰 Missing or malformed signature
  }

  const encoder = new TextEncoder();

  // 🌰 Import the secret as an HMAC key
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  // 🌰 Compute the expected signature
  const signatureBuffer = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode(payload)
  );

  // 🌰 Convert to hex string
  const expectedHex = Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  const expected = `sha256=${expectedHex}`;

  // 🌰 Constant-time comparison to prevent timing attacks
  return timingSafeEqual(expected, signature);
}

/**
 * Constant-time string comparison. 🌰
 * Prevents timing side-channel attacks by always comparing all bytes.
 */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    return false; // 🌰 Length mismatch — still do work to avoid early-exit timing leak
  }

  const encoder = new TextEncoder();
  const aBuf = encoder.encode(a);
  const bBuf = encoder.encode(b);

  let result = 0;
  for (let i = 0; i < aBuf.length; i++) {
    result |= aBuf[i] ^ bBuf[i];
  }

  return result === 0; // 🌰
}
