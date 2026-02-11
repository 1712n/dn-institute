import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_API_KEY = "test-api-key"

function makeHeaders(apiKey?: string): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (apiKey) headers["X-API-Key"] = apiKey
  return headers
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(),
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 Unauthorized when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders("wrong-key"),
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 for batch endpoint without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(),
      body: JSON.stringify({
        messages: [{ text: "hello", namespace: "test" }]
      })
    })
    expect(response.status).toBe(401)
  })
})

describe("Single message endpoint: POST /", () => {
  it("returns similarity score for valid input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ text: "hello world", namespace: "test" })
    })
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 for invalid text type", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ text: 123, namespace: "test" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ text: "hello" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 0 score when no matches found", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ text: "hello", namespace: "no-match" })
    })
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0)
  })
})

describe("Batch endpoint: POST /batch", () => {
  it("returns results for a valid batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [
          { text: "hello world", namespace: "test" },
          { text: "foo bar", namespace: "test" }
        ]
      })
    })
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: { similarity_score: number }[]
    }
    expect(json.results).toHaveLength(2)
    expect(json.results[0]).toHaveProperty("similarity_score")
    expect(json.results[1]).toHaveProperty("similarity_score")
  })

  it("handles duplicate texts in a batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [
          { text: "same text", namespace: "test" },
          { text: "same text", namespace: "test" },
          { text: "different text", namespace: "test" }
        ]
      })
    })
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: { similarity_score: number }[]
    }
    expect(json.results).toHaveLength(3)
    // Duplicate texts should produce identical scores in the same namespace
    expect(json.results[0].similarity_score).toBe(
      json.results[1].similarity_score
    )
  })

  it("handles messages with different namespaces", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [
          { text: "hello", namespace: "test" },
          { text: "hello", namespace: "no-match" }
        ]
      })
    })
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: { similarity_score: number }[]
    }
    expect(json.results).toHaveLength(2)
    expect(json.results[0].similarity_score).toBeGreaterThan(0)
    expect(json.results[1].similarity_score).toBe(0)
  })

  it("returns a single result for batch of one", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [{ text: "single", namespace: "test" }]
      })
    })
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: { similarity_score: number }[]
    }
    expect(json.results).toHaveLength(1)
  })

  it("returns 400 for empty messages array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ messages: [] })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty")
  })

  it("returns 400 when messages is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ messages: "not-an-array" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty")
  })

  it("returns 400 when messages field is missing", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ data: "wrong field" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty")
  })

  it("returns 400 when batch size exceeds maximum", async () => {
    const messages = Array.from({ length: 101 }, (_, i) => ({
      text: `message ${i}`,
      namespace: "test"
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ messages })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("exceeds maximum")
  })

  it("returns 400 when a message has invalid text type", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [
          { text: "valid", namespace: "test" },
          { text: 123, namespace: "test" }
        ]
      })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("index 1")
  })

  it("returns 400 when a message has empty text", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [{ text: "   ", namespace: "test" }]
      })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("index 0")
  })

  it("returns 400 when a message is missing namespace", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [{ text: "hello" }]
      })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("index 0")
  })
})
