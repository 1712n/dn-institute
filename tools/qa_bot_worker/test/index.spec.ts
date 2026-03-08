import { SELF } from "cloudflare:test";
import { describe, it, expect } from "vitest";

// Helper: generate a valid HMAC-SHA256 signature for testing
async function sign(payload: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
  const hex = [...new Uint8Array(sig)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return `sha256=${hex}`;
}

const WEBHOOK_SECRET = "test-webhook-secret";

describe("QA Bot Worker", () => {
  it("should return 200 on GET /", async () => {
    const response = await SELF.fetch("https://example.com/");
    expect(response.status).toBe(200);
    expect(await response.text()).toContain("QA Bot Worker is running");
  });

  it("should reject requests with invalid signature", async () => {
    const body = JSON.stringify({ action: "created" });
    const response = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      body,
      headers: {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=invalid",
        "X-GitHub-Event": "issue_comment",
      },
    });
    expect(response.status).toBe(401);
    expect(await response.text()).toBe("Invalid signature");
  });

  it("should accept valid webhook signature and ignore non-trigger comments", async () => {
    const payload = {
      action: "created",
      comment: { body: "Just a regular comment", user: { login: "tester" } },
      issue: { number: 1 },
      repository: { full_name: "owner/repo" },
    };
    const body = JSON.stringify(payload);
    const signature = await sign(body, WEBHOOK_SECRET);

    const response = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      body,
      headers: {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "issue_comment",
      },
    });
    expect(response.status).toBe(200);
    expect(await response.text()).toBe("No /articlecheck command");
  });

  it("should ignore issue_comment events that are not on PRs", async () => {
    const payload = {
      action: "created",
      comment: { body: "/articlecheck", user: { login: "tester" } },
      issue: { number: 1 },
      repository: { full_name: "owner/repo" },
    };
    const body = JSON.stringify(payload);
    const signature = await sign(body, WEBHOOK_SECRET);

    const response = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      body,
      headers: {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "issue_comment",
      },
    });
    expect(response.status).toBe(200);
    expect(await response.text()).toBe("Not a pull request comment");
  });

  it("should ignore pull_request events with non-trigger actions", async () => {
    const payload = {
      action: "closed",
      number: 42,
      pull_request: {
        url: "https://api.github.com/repos/owner/repo/pulls/42",
        diff_url: "https://github.com/owner/repo/pull/42.diff",
        number: 42,
      },
      repository: { full_name: "owner/repo" },
    };
    const body = JSON.stringify(payload);
    const signature = await sign(body, WEBHOOK_SECRET);

    const response = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      body,
      headers: {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "pull_request",
      },
    });
    expect(response.status).toBe(200);
    expect(await response.text()).toBe("PR action ignored");
  });

  it("should ignore unknown GitHub event types", async () => {
    const payload = { action: "completed" };
    const body = JSON.stringify(payload);
    const signature = await sign(body, WEBHOOK_SECRET);

    const response = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      body,
      headers: {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "check_run",
      },
    });
    expect(response.status).toBe(200);
    expect(await response.text()).toBe("Event ignored");
  });
});
