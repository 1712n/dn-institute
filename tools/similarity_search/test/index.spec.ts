import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key",
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing or invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header has wrong value", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key",
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("POST / (single message)", () => {
  it("returns similarity score for a valid request", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(200)
    const body = await response.json() as { similarity_score: number }
    expect(body).toHaveProperty("similarity_score")
    expect(typeof body.similarity_score).toBe("number")
  })

  it("returns 400 for invalid JSON format", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        text: 123,
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("POST /batch", () => {
  it("returns similarity scores for a valid batch request", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        messages: [
          { text: "First text", namespace: "ns1" },
          { text: "Second text", namespace: "ns2" },
        ]
      })
    })

    expect(response.status).toBe(200)
    const body = await response.json() as { results: { similarity_score: number }[] }
    expect(body.results).toHaveLength(2)
    expect(body.results[0]).toHaveProperty("similarity_score")
    expect(body.results[1]).toHaveProperty("similarity_score")
  })

  it("handles duplicate texts efficiently and returns correct order", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        messages: [
          { text: "Same text", namespace: "ns1" },
          { text: "Different text", namespace: "ns1" },
          { text: "Same text", namespace: "ns1" },
        ]
      })
    })

    expect(response.status).toBe(200)
    const body = await response.json() as { results: { similarity_score: number }[] }
    expect(body.results).toHaveLength(3)
    // Duplicate entries should have the same score
    expect(body.results[0].similarity_score).toBe(body.results[2].similarity_score)
  })

  it("returns 400 when messages is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ messages: "not an array" })
    })

    expect(response.status).toBe(400)
    const body = await response.json() as { error: string }
    expect(body.error).toBe("messages must be an array")
  })

  it("returns 400 when messages array is empty", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ messages: [] })
    })

    expect(response.status).toBe(400)
    const body = await response.json() as { error: string }
    expect(body.error).toBe("messages array must not be empty")
  })

  it("returns 400 when batch size exceeds maximum", async () => {
    const messages = Array.from({ length: 101 }, (_, i) => ({
      text: `Text ${i}`,
      namespace: "ns"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ messages })
    })

    expect(response.status).toBe(400)
    const body = await response.json() as { error: string }
    expect(body.error).toContain("batch size exceeds maximum")
  })

  it("returns 400 when a message has invalid format", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        messages: [
          { text: "Valid", namespace: "ns" },
          { text: 123, namespace: "ns" },
        ]
      })
    })

    expect(response.status).toBe(400)
    const body = await response.json() as { error: string }
    expect(body.error).toContain("invalid format at index 1")
  })

  it("requires authentication", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ text: "Test", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(401)
  })
})
