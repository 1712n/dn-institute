// 🌰 Tests for webhook signature verification 🌰

import { describe, it, expect } from "vitest";
import { verifyWebhookSignature } from "../src/crypto";

describe("🌰 verifyWebhookSignature", () => {
  it("🌰 rejects signatures without sha256= prefix", async () => {
    const result = await verifyWebhookSignature("payload", "invalid", "secret");
    expect(result).toBe(false);
  });

  it("🌰 verifies a valid HMAC-SHA256 signature", async () => {
    const payload = '{"test": "data"}';
    const secret = "test-secret";

    // 🌰 Compute the expected signature
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const mac = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
    const hex = Array.from(new Uint8Array(mac))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    const signature = `sha256=${hex}`;

    const result = await verifyWebhookSignature(payload, signature, secret);
    expect(result).toBe(true);
  });

  it("🌰 rejects an incorrect signature", async () => {
    const result = await verifyWebhookSignature(
      "payload",
      "sha256=0000000000000000000000000000000000000000000000000000000000000000",
      "secret",
    );
    expect(result).toBe(false);
  });
});
