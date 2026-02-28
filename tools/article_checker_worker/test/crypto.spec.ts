/**
 * 🌰 Tests for HMAC-SHA256 webhook signature verification
 */

import { describe, it, expect } from "vitest"
import { verifySignature } from "../src/crypto"

describe("verifySignature", () => {
  const secret = "test-webhook-secret"
  const payload = '{"action":"created"}'

  it("should verify a valid signature", async () => {
    // Generate a real signature for comparison
    const encoder = new TextEncoder()
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    )
    const signed = await crypto.subtle.sign("HMAC", key, encoder.encode(payload))
    const hex = Array.from(new Uint8Array(signed))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
    const signature = `sha256=${hex}`

    const result = await verifySignature(payload, signature, secret)
    expect(result).toBe(true)
  })

  it("should reject an invalid signature", async () => {
    const result = await verifySignature(payload, "sha256=invalid", secret)
    expect(result).toBe(false)
  })

  it("should reject a missing signature", async () => {
    const result = await verifySignature(payload, "", secret)
    expect(result).toBe(false)
  })

  it("should reject a signature without sha256= prefix", async () => {
    const result = await verifySignature(payload, "abc123", secret)
    expect(result).toBe(false)
  })

  it("should reject when payload is tampered", async () => {
    const encoder = new TextEncoder()
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    )
    const signed = await crypto.subtle.sign("HMAC", key, encoder.encode(payload))
    const hex = Array.from(new Uint8Array(signed))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
    const signature = `sha256=${hex}`

    const result = await verifySignature(
      '{"action":"deleted"}',
      signature,
      secret
    )
    expect(result).toBe(false)
  })
})
