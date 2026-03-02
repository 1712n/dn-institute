// 🌰 Test suite for similarity search API — single and batch endpoints
import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

// 🌰 Authentication tests
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
      headers: { "Content-Type": "application/json", "X-API-Key": "wrong-key" },
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 for batch endpoint without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: [{ text: "test", namespace: "ns" }] })
    })

    expect(response.status).toBe(401)
  })
})

// 🌰 Single endpoint tests
describe("POST / — single text similarity", () => {
  it("returns similarity score for valid input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 for missing text field", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ namespace: "test-namespace" })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 for missing namespace field", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "Sample text" })
    })

    expect(response.status).toBe(400)
  })
})

// 🌰 Batch endpoint tests
describe("POST /batch — batch similarity search", () => {
  it("returns results for a valid batch of items", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "First text", namespace: "ns-a" },
          { text: "Second text", namespace: "ns-b" }
        ]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    expect(json.results).toHaveLength(2)
    expect(json.results[0]).toHaveProperty("text", "First text")
    expect(json.results[0]).toHaveProperty("namespace", "ns-a")
    expect(json.results[0]).toHaveProperty("similarity_score")
    expect(json.results[1]).toHaveProperty("text", "Second text")
    expect(json.results[1]).toHaveProperty("namespace", "ns-b")
  })

  it("handles a single item in batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [{ text: "Only item", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ similarity_score: number }> }
    expect(json.results).toHaveLength(1)
    expect(typeof json.results[0].similarity_score).toBe("number")
  })

  it("deduplicates identical texts in batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "Same text", namespace: "ns-a" },
          { text: "Same text", namespace: "ns-b" },
          { text: "Same text", namespace: "ns-a" }
        ]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string }> }
    expect(json.results).toHaveLength(3)
    expect(json.results[0].namespace).toBe("ns-a")
    expect(json.results[1].namespace).toBe("ns-b")
    expect(json.results[2].namespace).toBe("ns-a")
  })

  it("returns 400 when items is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items: "not-an-array" })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("non-empty array")
  })

  it("returns 400 when items is empty", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items: [] })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("non-empty array")
  })

  it("returns 400 when batch exceeds maximum size", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `Text ${i}`,
      namespace: "ns"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("maximum of 100")
  })

  it("accepts exactly 100 items", async () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      text: `Text ${i}`,
      namespace: "ns"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: unknown[] }
    expect(json.results).toHaveLength(100)
  })

  it("returns 400 when item has non-string text", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [{ text: 123, namespace: "ns" }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 0")
  })

  it("returns 400 when item has non-string namespace", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [{ text: "valid", namespace: null }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 0")
  })

  it("returns 400 when item has empty text", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [{ text: "", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("empty")
  })

  it("validates all items and reports first invalid index", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "valid", namespace: "ns" },
          { text: "also valid", namespace: "ns" },
          { text: 42, namespace: "ns" }
        ]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 2")
  })
})
