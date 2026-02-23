/**
 * Verify GitHub webhook signature using HMAC-SHA256.
 * Uses Web Crypto API with timing-safe comparison.
 */
export async function verifySignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  if (!signature.startsWith("sha256=")) {
    return false
  }

  const sigHex = signature.slice("sha256=".length)

  const encoder = new TextEncoder()
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  )

  const signed = await crypto.subtle.sign("HMAC", key, encoder.encode(payload))
  const expectedHex = arrayBufferToHex(signed)

  return timingSafeEqual(sigHex, expectedHex)
}

function arrayBufferToHex(buffer: ArrayBuffer): string {
  return [...new Uint8Array(buffer)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
}

/**
 * Constant-time string comparison to prevent timing attacks.
 */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    return false
  }
  let result = 0
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return result === 0
}
