/**
 * 🌰 Tests for webhook signature verification 🌰
 */

import { describe, it, expect } from "vitest";
import { verifyWebhookSignature } from "../src/crypto";

describe("🌰 verifyWebhookSignature", () => {
  const secret = "test-webhook-secret-🌰";

  it("🌰 should accept a valid HMAC-SHA256 signature", async () => {
    const payload = '{"action":"created","comment":{"body":"/articlecheck"}}';

    // 🌰 Compute expected signature using Web Crypto
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );
    const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
    const hex = Array.from(new Uint8Array(sig))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    const signature = `sha256=${hex}`;

    const result = await verifyWebhookSignature(payload, signature, secret);
    expect(result).toBe(true); // 🌰
  });

  it("🌰 should reject an invalid signature", async () => {
    const payload = '{"test":"data"}';
    const signature = "sha256=0000000000000000000000000000000000000000000000000000000000000000";

    const result = await verifyWebhookSignature(payload, signature, secret);
    expect(result).toBe(false); // 🌰
  });

  it("🌰 should reject missing signature", async () => {
    const result = await verifyWebhookSignature('{"test":"data"}', "", secret);
    expect(result).toBe(false); // 🌰
  });

  it("🌰 should reject signature without sha256= prefix", async () => {
    const result = await verifyWebhookSignature(
      '{"test":"data"}',
      "invalid-format",
      secret
    );
    expect(result).toBe(false); // 🌰
  });
});
