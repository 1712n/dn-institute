/**
 * 🌰 Integration tests for cf-article-checker Cloudflare Worker
 *
 * Tests the webhook endpoint, permission checks, and error handling.
 * Uses Cloudflare Vitest pool-workers for realistic Workers runtime testing.
 */

import { SELF } from "cloudflare:test";
import { describe, it, expect } from "vitest";

import "../src/index";

// ─── Test Helpers ────────────────────────────────────────────────────────────

function createWebhookPayload(overrides: Record<string, unknown> = {}) {
  return {
    action: "created",
    comment: {
      body: "/articlecheck",
      user: { login: "testuser" },
      issue_url: "https://api.github.com/repos/1712n/dn-institute/issues/42",
    },
    issue: {
      pull_request: {
        url: "https://api.github.com/repos/1712n/dn-institute/pulls/42",
      },
      number: 42,
    },
    repository: {
      full_name: "1712n/dn-institute",
    },
    ...overrides,
  };
}

function webhookRequest(
  body: Record<string, unknown>,
  headers: Record<string, string> = {}
) {
  return new Request("https://example.com/webhook", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-GitHub-Event": "issue_comment",
      ...headers,
    },
    body: JSON.stringify(body),
  });
}

// ─── Health Check ────────────────────────────────────────────────────────────

describe("GET /", () => {
  it("returns health check message", async () => {
    const resp = await SELF.fetch("https://example.com/");
    expect(resp.status).toBe(200);
    expect(await resp.text()).toContain("Article Checker Worker is running");
  });
});

// ─── Webhook Event Filtering ─────────────────────────────────────────────────

describe("Webhook event filtering", () => {
  it("ignores non-issue_comment events", async () => {
    const resp = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Event": "push",
      },
      body: JSON.stringify({ action: "push" }),
    });

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Ignored event type");
  });

  it("ignores non-created actions", async () => {
    const payload = createWebhookPayload({ action: "deleted" });
    const resp = await SELF.fetch(
      webhookRequest(payload, { "X-GitHub-Event": "issue_comment" })
    );

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Ignored action");
  });

  it("ignores comments without /articlecheck command", async () => {
    const payload = createWebhookPayload();
    payload.comment.body = "This is a regular comment";
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("No /articlecheck command");
  });

  it("ignores comments on regular issues (not PRs)", async () => {
    const payload = createWebhookPayload();
    (payload.issue as Record<string, unknown>).pull_request = undefined;
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Not a pull request");
  });
});

// ─── Permission Checks ───────────────────────────────────────────────────────

describe("Permission checks", () => {
  it("rejects unauthorized users", async () => {
    const payload = createWebhookPayload();
    payload.comment.user.login = "random-user-not-in-reviewers";
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toContain("not an authorized reviewer");
  });

  it("accepts authorized reviewers (case-insensitive)", async () => {
    const payload = createWebhookPayload();
    payload.comment.user.login = "TestUser"; // REVIEWERS has "testuser"
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Article check triggered");
  });

  it("accepts second reviewer in the list", async () => {
    const payload = createWebhookPayload();
    payload.comment.user.login = "anotherreviewer";
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Article check triggered");
  });
});

// ─── Request Validation ──────────────────────────────────────────────────────

describe("Request validation", () => {
  it("returns 400 for invalid JSON body", async () => {
    const resp = await SELF.fetch("https://example.com/webhook", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Event": "issue_comment",
      },
      body: "not-valid-json{{{",
    });

    expect(resp.status).toBe(400);
    expect(await resp.text()).toBe("Invalid JSON");
  });
});

// ─── Webhook Trigger ─────────────────────────────────────────────────────────

describe("Webhook trigger", () => {
  it("triggers article check for valid request", async () => {
    const payload = createWebhookPayload();
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Article check triggered");
  });

  it("triggers for comments with /articlecheck among other text", async () => {
    const payload = createWebhookPayload();
    payload.comment.body = "Please review this article /articlecheck thanks!";
    const resp = await SELF.fetch(webhookRequest(payload));

    expect(resp.status).toBe(200);
    const json = (await resp.json()) as { message: string };
    expect(json.message).toBe("Article check triggered");
  });
});

// ─── Non-matching HTTP methods ───────────────────────────────────────────────

describe("HTTP method handling", () => {
  it("returns health check for GET on root", async () => {
    const resp = await SELF.fetch("https://example.com/");
    expect(resp.status).toBe(200);
  });
});
