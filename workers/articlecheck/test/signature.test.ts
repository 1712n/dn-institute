import { describe, expect, it } from "vitest";
import { verifyGitHubWebhookSignature } from "../common/src/github/webhook";

async function hmacHex(secret: string, payload: ArrayBuffer): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, payload);
  const bytes = new Uint8Array(mac);
  return [...bytes].map((b) => b.toString(16).padStart(2, "0")).join("");
}

describe("verifyGitHubWebhookSignature", () => {
  it("accepts a valid sha256 signature", async () => {
    const secret = "test-secret";
    const rawBody = new TextEncoder().encode(JSON.stringify({ hello: "world" })).buffer;
    const digest = await hmacHex(secret, rawBody);

    const res = await verifyGitHubWebhookSignature({
      headers: { event: "issue_comment", deliveryId: "d1", signature256: `sha256=${digest}` },
      secret,
      rawBody
    });
    expect(res.ok).toBe(true);
  });

  it("rejects an invalid signature", async () => {
    const secret = "test-secret";
    const rawBody = new TextEncoder().encode("x").buffer;
    const res = await verifyGitHubWebhookSignature({
      headers: { event: "issue_comment", deliveryId: "d1", signature256: "sha256=deadbeef" },
      secret,
      rawBody
    });
    expect(res.ok).toBe(false);
  });
});

