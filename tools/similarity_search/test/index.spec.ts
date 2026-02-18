import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
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
})

// 🌰 Single endpoint tests
describe("Single POST /", () => {
  it("returns similarity score for valid request", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
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

// 🌰 Batch endpoint tests
describe("POST /batch", () => {
  it("returns results for valid batch request", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "First text", namespace: "ns1" },
          { text: "Second text", namespace: "ns1" },
          { text: "Third text", namespace: "ns2" }
        ]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    expect(json.results).toHaveLength(3)
    expect(json.results[0]).toHaveProperty("text", "First text")
    expect(json.results[0]).toHaveProperty("namespace", "ns1")
    expect(json.results[0]).toHaveProperty("similarity_score")
    expect(json.results[2]).toHaveProperty("namespace", "ns2")
  })

  it("returns 400 for empty items array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items: [] })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 for missing items field", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "hello" })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 for invalid item format", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [{ text: 123, namespace: "ns1" }]
      })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when batch exceeds maximum size", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `Text ${i}`,
      namespace: "ns1"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(400)
    const text = await response.text()
    expect(text).toContain("100")
  })

  it("returns 401 when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: [{ text: "hello", namespace: "ns1" }]
      })
    })

    expect(response.status).toBe(401)
  })
})
