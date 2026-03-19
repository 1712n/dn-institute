import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

const NO_AUTH_HEADERS = {
  "Content-Type": "application/json"
}

// --- Authentication ---

describe("Authentication", () => {
  it("rejects requests without API key", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: NO_AUTH_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("rejects requests with wrong API key", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { ...NO_AUTH_HEADERS, "X-API-Key": "wrong-key" },
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.status).toBe(401)
  })

  it("accepts requests with valid API key", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.status).toBe(200)
  })
})

// --- Single endpoint ---

describe("POST / (single text)", () => {
  it("returns similarity score for valid input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "sample query", namespace: "articles" })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns 400 for missing text field", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ namespace: "articles" })
    })
    expect(response.status).toBe(400)
  })

  it("returns 400 for non-string text", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: 42, namespace: "articles" })
    })
    expect(response.status).toBe(400)
  })

  it("returns 400 for missing namespace", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "sample" })
    })
    expect(response.status).toBe(400)
  })

  it("handles empty string text gracefully", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "", namespace: "articles" })
    })
    // Empty string is still a valid string type
    expect(response.status).toBe(200)
  })

  it("handles special characters in text", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        text: 'text with "quotes" & <html> tags and unicode: 日本語',
        namespace: "articles"
      })
    })
    expect(response.status).toBe(200)
  })

  it("handles long text input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        text: "x".repeat(10000),
        namespace: "articles"
      })
    })
    expect(response.status).toBe(200)
  })
})

// --- Response format ---

describe("Response format", () => {
  it("returns JSON content type", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.headers.get("content-type")).toContain("application/json")
  })

  it("similarity score is between 0 and 1", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "market manipulation analysis", namespace: "articles" })
    })

    const json = await response.json() as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })
})

// --- HTTP methods ---

describe("HTTP methods", () => {
  it("rejects GET requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: VALID_HEADERS
    })
    // Hono returns 404 for unmatched routes
    expect(response.status).not.toBe(200)
  })

  it("rejects PUT requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.status).not.toBe(200)
  })
})

// --- Namespace isolation ---

describe("Namespace isolation", () => {
  it("queries with the provided namespace", async () => {
    const resp1 = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "same text", namespace: "namespace-a" })
    })

    const resp2 = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "same text", namespace: "namespace-b" })
    })

    expect(resp1.status).toBe(200)
    expect(resp2.status).toBe(200)

    // Both should return valid scores (mock returns same score regardless)
    const json1 = await resp1.json() as { similarity_score: number }
    const json2 = await resp2.json() as { similarity_score: number }
    expect(typeof json1.similarity_score).toBe("number")
    expect(typeof json2.similarity_score).toBe("number")
  })
})
