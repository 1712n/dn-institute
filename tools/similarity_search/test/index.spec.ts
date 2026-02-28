import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// 🌰 Helper: make an authenticated request
function authedFetch(url: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers)
  headers.set("X-API-Key", "test-api-key")
  headers.set("Content-Type", "application/json")
  return SELF.fetch(url, { ...init, headers })
}

// ──────────────────────────────────────────────────────
// 🌰 Authentication Tests
// ──────────────────────────────────────────────────────
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

  it("returns 401 for batch endpoint without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: [{ text: "hello", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(401)
  })
})

// ──────────────────────────────────────────────────────
// 🌰 Original Endpoint Tests (backward compatibility)
// ──────────────────────────────────────────────────────
describe("POST / (single item — backward compatible)", () => {
  it("returns similarity_score for valid input", async () => {
    const response = await authedFetch("https://example.com/", {
      method: "POST",
      body: JSON.stringify({ text: "some text", namespace: "test-ns" })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 for invalid format", async () => {
    const response = await authedFetch("https://example.com/", {
      method: "POST",
      body: JSON.stringify({ text: 123, namespace: "test-ns" })
    })

    expect(response.status).toBe(400)
  })
})

// ──────────────────────────────────────────────────────
// 🌰 Batch Endpoint Tests
// ──────────────────────────────────────────────────────
describe("POST /batch", () => {
  // ── Valid Requests ──────────────────────────────────

  it("returns results for a valid batch request", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [
          { text: "first text", namespace: "ns-a" },
          { text: "second text", namespace: "ns-b" }
        ]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    expect(json.results).toHaveLength(2)
    expect(json.results[0]).toEqual({
      text: "first text",
      namespace: "ns-a",
      similarity_score: expect.any(Number)
    })
    expect(json.results[1]).toEqual({
      text: "second text",
      namespace: "ns-b",
      similarity_score: expect.any(Number)
    })
  })

  it("handles single-item batch correctly", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: "only item", namespace: "single-ns" }]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    expect(json.results).toHaveLength(1)
    expect(json.results[0].text).toBe("only item")
    expect(json.results[0].namespace).toBe("single-ns")
  })

  it("preserves original request order in results", async () => {
    const items = [
      { text: "alpha", namespace: "ns-1" },
      { text: "beta", namespace: "ns-2" },
      { text: "gamma", namespace: "ns-1" },
      { text: "delta", namespace: "ns-3" }
    ]

    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string }> }
    expect(json.results).toHaveLength(4)
    expect(json.results[0].text).toBe("alpha")
    expect(json.results[1].text).toBe("beta")
    expect(json.results[2].text).toBe("gamma")
    expect(json.results[3].text).toBe("delta")
  })

  it("handles duplicate namespaces within a batch", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [
          { text: "text one", namespace: "same-ns" },
          { text: "text two", namespace: "same-ns" },
          { text: "text three", namespace: "same-ns" }
        ]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    expect(json.results).toHaveLength(3)
    for (const result of json.results) {
      expect(result.namespace).toBe("same-ns")
      expect(typeof result.similarity_score).toBe("number")
    }
  })

  it("returns numeric similarity_score for each result item", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: "test text", namespace: "ns" }]
      })
    })

    const json = await response.json() as { results: Array<{ similarity_score: number }> }
    expect(json.results[0].similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.results[0].similarity_score).toBeLessThanOrEqual(1)
  })

  // ── Validation Errors ──────────────────────────────

  it("returns structured error for missing items array", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ data: "not items" })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("MISSING_ITEMS")
    expect(json.error).toContain("items")
  })

  it("returns structured error for empty batch", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ items: [] })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("EMPTY_BATCH")
  })

  it("returns structured error when batch exceeds MAX_BATCH_SIZE", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `text ${i}`,
      namespace: "ns"
    }))

    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string; details?: string }
    expect(json.code).toBe("BATCH_TOO_LARGE")
    expect(json.details).toContain("101")
  })

  it("returns structured error for invalid item types", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: 42, namespace: "ns" }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("INVALID_ITEM")
    expect(json.error).toContain("index 0")
  })

  it("returns structured error for empty text string", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: "", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("EMPTY_TEXT")
  })

  it("returns structured error for text exceeding MAX_TEXT_LENGTH", async () => {
    const longText = "a".repeat(10_001)
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: longText, namespace: "ns" }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("TEXT_TOO_LONG")
  })

  it("returns structured error for invalid JSON body", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: "not-json-at-all"
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("INVALID_JSON")
  })

  it("validates item at correct index in batch", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [
          { text: "valid", namespace: "ns" },
          { text: "also valid", namespace: "ns" },
          { text: 999, namespace: "ns" }
        ]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string; details?: string }
    expect(json.code).toBe("INVALID_ITEM")
    expect(json.error).toContain("index 2")
  })

  it("rejects items array with non-string namespace", async () => {
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: "hello", namespace: 123 }]
      })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string; code: string }
    expect(json.code).toBe("INVALID_ITEM")
  })

  it("accepts exactly MAX_BATCH_SIZE items", async () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      text: `text ${i}`,
      namespace: "ns"
    }))

    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<unknown> }
    expect(json.results).toHaveLength(100)
  })

  it("handles items with text at exactly MAX_TEXT_LENGTH", async () => {
    const exactText = "b".repeat(10_000)
    const response = await authedFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        items: [{ text: exactText, namespace: "ns" }]
      })
    })

    expect(response.status).toBe(200)
  })
})
