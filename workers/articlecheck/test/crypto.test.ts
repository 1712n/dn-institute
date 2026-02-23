import { describe, it, expect, beforeAll } from "vitest"
import { webcrypto } from "node:crypto"
import { verifySignature } from "../src/crypto"

// Polyfill crypto.subtle for Node.js test environment
beforeAll(() => {
  if (typeof globalThis.crypto === "undefined") {
    // @ts-expect-error - Node.js webcrypto is compatible enough
    globalThis.crypto = webcrypto
  }
})

describe("verifySignature", () => {
  it("returns true for a valid signature", async () => {
    const payload = '{"action":"created"}'
    const secret = "test-secret"

    // Generate a valid signature using the same Web Crypto API
    const encoder = new TextEncoder()
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    )
    const signed = await crypto.subtle.sign(
      "HMAC",
      key,
      encoder.encode(payload)
    )
    const hex = [...new Uint8Array(signed)]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
    const signature = `sha256=${hex}`

    const result = await verifySignature(payload, signature, secret)
    expect(result).toBe(true)
  })

  it("returns false for an invalid signature", async () => {
    const result = await verifySignature(
      '{"action":"created"}',
      "sha256=0000000000000000000000000000000000000000000000000000000000000000",
      "test-secret"
    )
    expect(result).toBe(false)
  })

  it("returns false for a signature without sha256= prefix", async () => {
    const result = await verifySignature(
      '{"action":"created"}',
      "invalid-signature",
      "test-secret"
    )
    expect(result).toBe(false)
  })

  it("returns false for empty signature", async () => {
    const result = await verifySignature(
      '{"action":"created"}',
      "",
      "test-secret"
    )
    expect(result).toBe(false)
  })
})
