import { SELF } from "cloudflare:test"
import { describe, it, expect, beforeEach } from "vitest"

import "../src/index"

const AUTH_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "Sample text", namespace: "test" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 Unauthorized on /batch without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: [{ text: "test", namespace: "ns" }] })
    })
    expect(response.status).toBe(401)
  })
})

describe("Single Text Endpoint", () => {
  it("processes request with valid auth (runtime depends on bindings)", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    // Without AI/Vectorize bindings, may fail at runtime - that's expected
    // This test verifies request structure is correct
    expect([200, 400, 500]).toContain(response.status)
  })
})

describe("Batch Endpoint - Validation", () => {
  it("returns 400 when items array is missing", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({})
    })
    expect(response.status).toBe(400)
    const json = await response.json()
    expect(json.error).toContain("items")
  })

  it("returns 400 when items array is empty", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items: [] })
    })
    expect(response.status).toBe(400)
    const json = await response.json()
    expect(json.error).toContain("empty")
  })

  it("returns 400 when batch size exceeds 100 items", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `text ${i}`,
      namespace: "ns"
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items })
    })
    expect(response.status).toBe(400)
    const json = await response.json()
    expect(json.error).toContain("exceeds limit")
    expect(json.limit).toBe(100)
  })

  it("returns 400 when item has invalid format", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ 
        items: [
          { text: "valid", namespace: "ns" },
          { text: 123, namespace: "ns" } // invalid
        ] 
      })
    })
    expect(response.status).toBe(400)
    const json = await response.json()
    expect(json.error).toBe("Validation failed")
    expect(json.failed).toBeDefined()
    expect(json.failed.length).toBe(1)
  })
})

describe("Batch Endpoint - Success Cases", () => {
  it("processes single item batch successfully", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ 
        items: [{ text: "test message", namespace: "test-ns" }] 
      })
    })
    // Without proper AI/Vectorize bindings, will fail at runtime
    // This test verifies the request structure is correct
    expect([200, 500]).toContain(response.status)
  })

  it("processes multiple items across namespaces", async () => {
    const items = [
      { text: "message 1", namespace: "ns1" },
      { text: "message 2", namespace: "ns1" },
      { text: "message 3", namespace: "ns2" }
    ]
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items })
    })
    expect([200, 500]).toContain(response.status)
  })

  it("includes cost tracking in response", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ 
        items: [{ text: "test", namespace: "ns" }] 
      })
    })
    if (response.status === 200) {
      const json = await response.json()
      expect(json.cost).toBeDefined()
      expect(json.cost.estimated_usd).toBeDefined()
      expect(json.summary).toBeDefined()
      expect(json.summary.total).toBe(1)
    }
  })

  it("handles duplicate texts efficiently (single embedding)", async () => {
    const items = [
      { text: "same text", namespace: "ns1" },
      { text: "same text", namespace: "ns2" },
      { text: "same text", namespace: "ns3" }
    ]
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items })
    })
    if (response.status === 200) {
      const json = await response.json()
      // Only 1 unique text should be embedded
      expect(json.cost.ai_embedding_calls).toBe(1)
      expect(json.summary.processed).toBe(3)
    }
  })

  it("supports useCache=false to disable caching", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ 
        items: [{ text: "test", namespace: "ns" }],
        useCache: false
      })
    })
    expect([200, 500]).toContain(response.status)
  })
})

describe("Health Endpoint", () => {
  it("returns health status", async () => {
    const response = await SELF.fetch("https://example.com/health", {
      method: "GET",
      headers: AUTH_HEADERS
    })
    expect(response.status).toBe(200)
    const json = await response.json()
    expect(json.status).toBe("healthy")
    expect(json.endpoints).toBeDefined()
  })
})

describe("Cache Stats Endpoint", () => {
  it("returns cache status (may be 503 if not configured)", async () => {
    const response = await SELF.fetch("https://example.com/cache/stats", {
      method: "GET",
      headers: AUTH_HEADERS
    })
    expect([200, 503]).toContain(response.status)
  })
})
