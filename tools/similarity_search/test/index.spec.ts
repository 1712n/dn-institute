import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// 🌰 Helper to make authenticated requests
function authFetch(url: string, options: RequestInit = {}) {
  return SELF.fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "test-api-key",
      ...(options.headers || {})
    }
  })
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

  it("returns 401 Unauthorized for batch endpoint without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        entries: [{ text: "Sample text", namespace: "test-namespace" }]
      })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// 🌰 Single entry endpoint tests
describe("Single similarity search", () => {
  it("returns a similarity score for valid input", async () => {
    const response = await authFetch("https://example.com/", {
      method: "POST",
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 for invalid input types", async () => {
    const response = await authFetch("https://example.com/", {
      method: "POST",
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
describe("Batch similarity search", () => {
  it("returns similarity scores for multiple entries", async () => {
    const response = await authFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        entries: [
          { text: "First text", namespace: "ns1" },
          { text: "Second text", namespace: "ns2" },
          { text: "Third text", namespace: "ns1" }
        ]
      })
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: Array<{ text: string; namespace: string; similarity_score: number }>
    }
    expect(json.results).toHaveLength(3)
    json.results.forEach((result, i) => {
      expect(result).toHaveProperty("similarity_score")
      expect(typeof result.similarity_score).toBe("number")
      expect(result).toHaveProperty("text")
      expect(result).toHaveProperty("namespace")
    })
  })

  it("returns empty results array for empty entries", async () => {
    const response = await authFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ entries: [] })
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { results: Array<unknown> }
    expect(json.results).toHaveLength(0)
  })

  it("returns 400 when entries is not an array", async () => {
    const response = await authFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ entries: "not-an-array" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe(
      "Invalid JSON format: 'entries' must be an array"
    )
  })

  it("returns 400 when an entry has invalid types", async () => {
    const response = await authFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        entries: [
          { text: "Valid text", namespace: "ns1" },
          { text: 42, namespace: "ns2" }
        ]
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format at entry index 1")
  })

  it("returns 400 when batch size exceeds maximum", async () => {
    const entries = Array.from({ length: 101 }, (_, i) => ({
      text: `Text ${i}`,
      namespace: "ns"
    }))

    const response = await authFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({ entries })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe(
      "Batch size exceeds maximum of 100 entries"
    )
  })

  it("handles single entry batch correctly", async () => {
    const response = await authFetch("https://example.com/batch", {
      method: "POST",
      body: JSON.stringify({
        entries: [{ text: "Only one", namespace: "ns1" }]
      })
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as {
      results: Array<{ text: string; namespace: string; similarity_score: number }>
    }
    expect(json.results).toHaveLength(1)
    expect(json.results[0].text).toBe("Only one")
    expect(json.results[0].namespace).toBe("ns1")
  })
})
