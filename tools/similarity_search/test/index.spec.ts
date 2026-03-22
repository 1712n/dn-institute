import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// 🌰 Helper to build request with auth
function authedRequest(
  path: string,
  body: unknown
): [string, RequestInit] {
  return [
    `https://example.com${path}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify(body)
    }
  ]
}

// 🌰 Authentication tests — apply to all endpoints
describe("Authentication", () => {
  it("returns 401 when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
      },
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 for /batch when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: [{ text: "test", namespace: "ns" }]
      })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// 🌰 Single-text endpoint tests
describe("POST / (single)", () => {
  it("returns similarity score for valid input", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/", { text: "hello world", namespace: "test" })
    )
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 for invalid JSON format", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/", { text: 123, namespace: "test" })
    )
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

// 🌰 Batch endpoint tests
describe("POST /batch", () => {
  it("returns results for valid batch input", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [
          { text: "first document", namespace: "articles" },
          { text: "second document", namespace: "articles" }
        ]
      })
    )
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: Array<{
        text: string
        namespace: string
        similarity_score: number
      }>
    }
    expect(json.results).toHaveLength(2)
    expect(json.results[0]).toHaveProperty("text", "first document")
    expect(json.results[0]).toHaveProperty("namespace", "articles")
    expect(typeof json.results[0].similarity_score).toBe("number")
    expect(json.results[1]).toHaveProperty("text", "second document")
  })

  it("handles single-item batch", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [{ text: "only one", namespace: "ns" }]
      })
    )
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: Array<{ similarity_score: number }>
    }
    expect(json.results).toHaveLength(1)
    expect(typeof json.results[0].similarity_score).toBe("number")
  })

  it("deduplicates identical texts across different namespaces", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [
          { text: "same text", namespace: "ns-a" },
          { text: "same text", namespace: "ns-b" },
          { text: "different text", namespace: "ns-a" }
        ]
      })
    )
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: Array<{
        text: string
        namespace: string
        similarity_score: number
      }>
    }
    // 🌰 All 3 items returned despite text deduplication
    expect(json.results).toHaveLength(3)
    expect(json.results[0].namespace).toBe("ns-a")
    expect(json.results[1].namespace).toBe("ns-b")
  })

  // 🌰 Validation tests
  it("returns 400 when items is not an array", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", { items: "not an array" })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toBe("items must be a non-empty array")
  })

  it("returns 400 when items is empty", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", { items: [] })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toBe("items must be a non-empty array")
  })

  it("returns 400 when items is missing", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {})
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toBe("items must be a non-empty array")
  })

  it("returns 400 when batch exceeds maximum size", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "ns"
    }))
    const response = await SELF.fetch(
      ...authedRequest("/batch", { items })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toBe("Batch size exceeds maximum of 100")
  })

  it("returns 400 when item text is not a string", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [{ text: 42, namespace: "ns" }]
      })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toContain("Invalid item at index 0")
    expect(json.error).toContain("text must be a non-empty string")
  })

  it("returns 400 when item text is empty", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [{ text: "   ", namespace: "ns" }]
      })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toContain("Invalid item at index 0")
  })

  it("returns 400 when item namespace is not a string", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [{ text: "hello", namespace: 123 }]
      })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toContain("Invalid item at index 0")
    expect(json.error).toContain("namespace must be a non-empty string")
  })

  it("returns 400 with correct index for invalid item in middle of batch", async () => {
    const response = await SELF.fetch(
      ...authedRequest("/batch", {
        items: [
          { text: "valid", namespace: "ns" },
          { text: "also valid", namespace: "ns" },
          { text: "", namespace: "ns" }
        ]
      })
    )
    expect(response.status).toBe(400)
    const json = (await response.json()) as { error: string }
    expect(json.error).toContain("Invalid item at index 2")
  })

  it("accepts exactly 100 items (boundary)", async () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "ns"
    }))
    const response = await SELF.fetch(
      ...authedRequest("/batch", { items })
    )
    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: Array<{ similarity_score: number }>
    }
    expect(json.results).toHaveLength(100)
  })
})
