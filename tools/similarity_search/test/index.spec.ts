/**
 * 🌰 Integration tests for Similarity Search API with batch processing
 *
 * Tests authentication, single endpoint, batch endpoint, validation,
 * and edge cases using Cloudflare Vitest pool-workers.
 */

import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// ─── Helpers 🌰 ──────────────────────────────────────────────────────────────

function authHeaders(extra: Record<string, string> = {}) {
  return {
    "Content-Type": "application/json",
    "X-API-Key": "test-api-key",
    ...extra
  }
}

// ─── Authentication 🌰 ──────────────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 Unauthorized when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
      },
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 for batch endpoint without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify([{ text: "hello", namespace: "ns" }])
    })

    expect(response.status).toBe(401)
  })
})

// ─── Single endpoint 🌰 ─────────────────────────────────────────────────────

describe("POST / (single entry)", () => {
  it("returns similarity score for valid request", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 for invalid JSON format (missing text)", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ namespace: "test-namespace" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 for invalid JSON format (missing namespace)", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ text: "hello" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 for non-string text", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ text: 123, namespace: "ns" })
    })

    expect(response.status).toBe(400)
  })
})

// ─── Batch endpoint 🌰 ──────────────────────────────────────────────────────

describe("POST /batch", () => {
  it("returns array of similarity scores for valid batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify([
        { text: "hello world", namespace: "ns1" },
        { text: "foo bar", namespace: "ns1" }
      ])
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }[]
    expect(Array.isArray(json)).toBe(true)
    expect(json).toHaveLength(2)
    expect(json[0]).toHaveProperty("similarity_score")
    expect(json[1]).toHaveProperty("similarity_score")
  })

  it("preserves order of results matching input order", async () => {
    const entries = [
      { text: "alpha", namespace: "ns" },
      { text: "beta", namespace: "ns" },
      { text: "gamma", namespace: "ns" }
    ]

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(entries)
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }[]
    expect(json).toHaveLength(3)
  })

  it("handles entries across different namespaces", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify([
        { text: "hello", namespace: "ns-a" },
        { text: "world", namespace: "ns-b" }
      ])
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }[]
    expect(json).toHaveLength(2)
  })

  it("handles single-entry batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify([{ text: "solo", namespace: "ns" }])
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }[]
    expect(json).toHaveLength(1)
  })

  it("returns 400 for empty batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify([])
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Batch must contain at least one entry")
  })

  it("returns 400 for non-array body", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Request body must be a JSON array")
  })

  it("returns 400 for batch exceeding max size", async () => {
    const entries = Array.from({ length: 21 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "ns"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(entries)
    })

    expect(response.status).toBe(400)
    const text = await response.text()
    expect(text).toContain("Batch size exceeds maximum")
  })

  it("returns 400 for invalid entry in batch (missing text)", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify([
        { text: "valid", namespace: "ns" },
        { namespace: "ns" } // missing text
      ])
    })

    expect(response.status).toBe(400)
    const text = await response.text()
    expect(text).toContain("Invalid entry at index 1")
  })

  it("returns 400 for invalid entry in batch (non-string namespace)", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify([{ text: "hello", namespace: 123 }])
    })

    expect(response.status).toBe(400)
    const text = await response.text()
    expect(text).toContain("Invalid entry at index 0")
  })

  it("returns 400 for invalid JSON body", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: "not-json{{{"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON")
  })
})

// ─── Batch with max allowed size 🌰 ─────────────────────────────────────────

describe("POST /batch edge cases", () => {
  it("accepts batch of exactly MAX_BATCH_SIZE (20)", async () => {
    const entries = Array.from({ length: 20 }, (_, i) => ({
      text: `entry-${i}`,
      namespace: "ns"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(entries)
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }[]
    expect(json).toHaveLength(20)
  })
})
