import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

// 🌰 Helper for batch requests
function batchRequest(items: unknown[], headers = VALID_HEADERS) {
  return SELF.fetch("https://example.com/batch", {
    method: "POST",
    headers,
    body: JSON.stringify({ items })
  })
}

// ── Authentication 🌰 ──────────────────────────────────────────────

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

  it("returns 401 for batch endpoint when API key is missing", async () => {
    const response = await batchRequest(
      [{ text: "test", namespace: "ns" }],
      { "Content-Type": "application/json" }
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 for batch endpoint when API key is wrong", async () => {
    const response = await batchRequest(
      [{ text: "test", namespace: "ns" }],
      { "Content-Type": "application/json", "X-API-Key": "wrong-key" }
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// ── Single endpoint (backward compatibility) 🌰 ────────────────────

describe("Single endpoint", () => {
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

// ── Batch endpoint — validation 🌰 ─────────────────────────────────

describe("Batch endpoint - validation", () => {
  it("returns 400 when items is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items: "not-an-array" })
    })

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toBe("items must be a non-empty array")
  })

  it("returns 400 when items array is empty", async () => {
    const response = await batchRequest([])

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toBe("items must be a non-empty array")
  })

  it("returns 400 when batch exceeds maximum size", async () => {
    const oversized = Array.from({ length: 101 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "ns"
    }))
    const response = await batchRequest(oversized)

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toBe("Batch size exceeds maximum of 100")
  })

  it("returns 400 with index when text is not a string", async () => {
    const response = await batchRequest([
      { text: "valid", namespace: "ns" },
      { text: 42, namespace: "ns" }
    ])

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 1")
    expect(json.error).toContain("must be strings")
  })

  it("returns 400 with index when namespace is not a string", async () => {
    const response = await batchRequest([
      { text: "valid", namespace: null }
    ])

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 0")
  })

  it("returns 400 when text is empty string", async () => {
    const response = await batchRequest([
      { text: "", namespace: "ns" }
    ])

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 0")
    expect(json.error).toContain("must not be empty")
  })

  it("returns 400 when text exceeds maximum length", async () => {
    const longText = "a".repeat(10_001)
    const response = await batchRequest([
      { text: longText, namespace: "ns" }
    ])

    expect(response.status).toBe(400)
    const json = await response.json() as { error: string }
    expect(json.error).toContain("index 0")
    expect(json.error).toContain("exceeds maximum length")
  })
})

// ── Batch endpoint — processing 🌰 ─────────────────────────────────

describe("Batch endpoint - processing", () => {
  it("returns results for a single-item batch", async () => {
    const response = await batchRequest([
      { text: "hello world", namespace: "ns1" }
    ])

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ similarity_score: number }> }
    expect(json.results).toHaveLength(1)
    expect(typeof json.results[0].similarity_score).toBe("number")
  })

  it("returns results for multi-item batch", async () => {
    const response = await batchRequest([
      { text: "first message", namespace: "ns1" },
      { text: "second message", namespace: "ns2" },
      { text: "third message", namespace: "ns1" }
    ])

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    expect(json.results).toHaveLength(3)
    // Verify input order is preserved 🌰
    expect(json.results[0].text).toBe("first message")
    expect(json.results[1].text).toBe("second message")
    expect(json.results[2].text).toBe("third message")
  })

  it("preserves input order across different namespaces", async () => {
    const items = [
      { text: "a", namespace: "z-namespace" },
      { text: "b", namespace: "a-namespace" },
      { text: "c", namespace: "z-namespace" },
      { text: "d", namespace: "a-namespace" }
    ]
    const response = await batchRequest(items)

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string }> }
    expect(json.results.map((r) => r.text)).toEqual(["a", "b", "c", "d"])
    expect(json.results.map((r) => r.namespace)).toEqual([
      "z-namespace", "a-namespace", "z-namespace", "a-namespace"
    ])
  })

  it("handles duplicate texts efficiently via deduplication", async () => {
    const response = await batchRequest([
      { text: "duplicate", namespace: "ns1" },
      { text: "duplicate", namespace: "ns2" },
      { text: "duplicate", namespace: "ns1" }
    ])

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ similarity_score: number }> }
    expect(json.results).toHaveLength(3)
    // All should return valid scores despite sharing the same text 🌰
    for (const result of json.results) {
      expect(typeof result.similarity_score).toBe("number")
    }
  })

  it("processes the maximum batch size of 100 items", async () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      text: `message-${i}`,
      namespace: "ns"
    }))
    const response = await batchRequest(items)

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string }> }
    expect(json.results).toHaveLength(100)
    // Verify order preserved across full batch 🌰
    expect(json.results[0].text).toBe("message-0")
    expect(json.results[99].text).toBe("message-99")
  })

  it("includes text and namespace in each result", async () => {
    const response = await batchRequest([
      { text: "check fields", namespace: "my-ns" }
    ])

    expect(response.status).toBe(200)
    const json = await response.json() as { results: Array<{ text: string; namespace: string; similarity_score: number }> }
    const result = json.results[0]
    expect(result.text).toBe("check fields")
    expect(result.namespace).toBe("my-ns")
    expect(result).toHaveProperty("similarity_score")
  })
})
