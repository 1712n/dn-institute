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

// 🌰 Authentication tests
describe("Authentication", () => {
  it("returns 401 when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: NO_AUTH_HEADERS,
      body: JSON.stringify({ text: "hello", namespace: "test" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": "wrong-key" },
      body: JSON.stringify({ text: "hello", namespace: "test" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 on batch endpoint without auth", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: NO_AUTH_HEADERS,
      body: JSON.stringify({ items: [{ text: "hello", namespace: "test" }] })
    })
    expect(response.status).toBe(401)
  })
})

// 🌰 Single endpoint tests
describe("POST /", () => {
  it("returns similarity score for valid input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "sample text", namespace: "test-ns" })
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
      body: JSON.stringify({ text: 123, namespace: "test" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "hello" })
    })
    expect(response.status).toBe(400)
  })
})

// 🌰 Batch endpoint tests
describe("POST /batch", () => {
  it("returns results for valid batch input", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "first text", namespace: "ns1" },
          { text: "second text", namespace: "ns2" }
        ]
      })
    })
    expect(response.status).toBe(200)
    const json = await response.json() as { results: any[] }
    expect(json.results).toHaveLength(2)
    expect(json.results[0]).toHaveProperty("similarity_score")
    expect(json.results[0]).toHaveProperty("text", "first text")
    expect(json.results[0]).toHaveProperty("namespace", "ns1")
    expect(json.results[1]).toHaveProperty("text", "second text")
    expect(json.results[1]).toHaveProperty("namespace", "ns2")
  })

  it("handles items in the same namespace", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "aaa", namespace: "shared" },
          { text: "bbb", namespace: "shared" },
          { text: "ccc", namespace: "shared" }
        ]
      })
    })
    expect(response.status).toBe(200)
    const json = await response.json() as { results: any[] }
    expect(json.results).toHaveLength(3)
    json.results.forEach((r: any) => {
      expect(r.namespace).toBe("shared")
      expect(typeof r.similarity_score).toBe("number")
    })
  })

  it("returns 400 when items is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items: "not-an-array" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty array")
  })

  it("returns 400 when items is empty", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items: [] })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty array")
  })

  it("returns 400 when batch exceeds max size", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "ns"
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("exceeds maximum")
  })

  it("returns 400 when an item has invalid format", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "valid", namespace: "ns" },
          { text: 999, namespace: "ns" }
        ]
      })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("index 1")
  })

  it("accepts exactly 100 items (max batch size)", async () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "ns"
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ items })
    })
    expect(response.status).toBe(200)
    const json = await response.json() as { results: any[] }
    expect(json.results).toHaveLength(100)
  })
})
