/**
 * 🌰 Tests for the main Hono app (webhook routing)
 */

import { describe, it, expect, vi, beforeEach } from "vitest"
import app from "../src/index"
import type { Env } from "../src/types"

// Mock environment bindings
const mockEnv: Env = {
  WEBHOOK_SECRET: "test-secret",
  GITHUB_TOKEN: "ghp_test",
  ANTHROPIC_API_KEY: "sk-ant-test",
  BRAVE_API_KEY: "BSA-test",
  REVIEWER_ALLOWLIST: '["testuser"]',
}

// Helper to generate valid HMAC signature
async function signPayload(payload: string, secret: string): Promise<string> {
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
  return `sha256=${hex}`
}

describe("GET /", () => {
  it("should return health check", async () => {
    const res = await app.request("/", {}, mockEnv)
    expect(res.status).toBe(200)
    const json = await res.json()
    expect(json).toEqual({
      status: "ok",
      service: "article-checker-worker",
      version: "1.0.0",
    })
  })
})

describe("POST /webhook", () => {
  it("should reject requests without valid signature", async () => {
    const body = '{"action":"created"}'
    const res = await app.request(
      "/webhook",
      {
        method: "POST",
        body,
        headers: {
          "Content-Type": "application/json",
          "X-Hub-Signature-256": "sha256=invalid",
        },
      },
      mockEnv
    )
    expect(res.status).toBe(401)
  })

  it("should reject requests without signature header", async () => {
    const body = '{"action":"created"}'
    const res = await app.request(
      "/webhook",
      {
        method: "POST",
        body,
        headers: { "Content-Type": "application/json" },
      },
      mockEnv
    )
    expect(res.status).toBe(401)
  })

  it("should skip non-PR comments with 200", async () => {
    const payload = JSON.stringify({
      action: "created",
      issue: { number: 1 },
      comment: {
        id: 1,
        body: "/articlecheck",
        user: { login: "testuser" },
      },
      repository: {
        full_name: "owner/repo",
        owner: { login: "owner" },
        name: "repo",
      },
      sender: { login: "testuser" },
    })

    const signature = await signPayload(payload, mockEnv.WEBHOOK_SECRET)
    const res = await app.request(
      "/webhook",
      {
        method: "POST",
        body: payload,
        headers: {
          "Content-Type": "application/json",
          "X-Hub-Signature-256": signature,
        },
      },
      mockEnv
    )
    expect(res.status).toBe(200)
    const json = await res.json()
    expect(json.status).toBe("skipped")
    expect(json.reason).toContain("not on a pull request")
  })

  it("should skip comments without /articlecheck", async () => {
    const payload = JSON.stringify({
      action: "created",
      issue: {
        number: 1,
        pull_request: { url: "https://api.github.com/repos/o/r/pulls/1" },
      },
      comment: {
        id: 1,
        body: "LGTM!",
        user: { login: "testuser" },
      },
      repository: {
        full_name: "owner/repo",
        owner: { login: "owner" },
        name: "repo",
      },
      sender: { login: "testuser" },
    })

    const signature = await signPayload(payload, mockEnv.WEBHOOK_SECRET)
    const res = await app.request(
      "/webhook",
      {
        method: "POST",
        body: payload,
        headers: {
          "Content-Type": "application/json",
          "X-Hub-Signature-256": signature,
        },
      },
      mockEnv
    )
    expect(res.status).toBe(200)
    const json = await res.json()
    expect(json.status).toBe("skipped")
  })

  it("should skip non-allowed reviewers", async () => {
    const payload = JSON.stringify({
      action: "created",
      issue: {
        number: 1,
        pull_request: { url: "https://api.github.com/repos/o/r/pulls/1" },
      },
      comment: {
        id: 1,
        body: "/articlecheck",
        user: { login: "unauthorized-user" },
      },
      repository: {
        full_name: "owner/repo",
        owner: { login: "owner" },
        name: "repo",
      },
      sender: { login: "unauthorized-user" },
    })

    const signature = await signPayload(payload, mockEnv.WEBHOOK_SECRET)
    const res = await app.request(
      "/webhook",
      {
        method: "POST",
        body: payload,
        headers: {
          "Content-Type": "application/json",
          "X-Hub-Signature-256": signature,
        },
      },
      mockEnv
    )
    expect(res.status).toBe(200)
    const json = await res.json()
    expect(json.status).toBe("skipped")
    expect(json.reason).toContain("allowlist")
  })
})
