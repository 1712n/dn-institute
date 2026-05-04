import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const AUTH_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key",
}

// ─── Existing single-item auth test ──────────────────────────────────

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing or invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace",
      }),
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// ─── Batch endpoint tests ────────────────────────────────────────────

describe("Batch Processing - /batch", () => {
  // --- Authentication ---

  it("returns 401 when API key is missing on /batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: [{ text: "test", namespace: "ns" }],
      }),
    })
    expect(response.status).toBe(401)
  })

  // --- Input validation ---

  it("returns 400 when items is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items: "not-an-array" }),
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty array")
  })

  it("returns 400 when items is empty", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items: [] }),
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty array")
  })

  it("returns 400 when batch exceeds maximum size", async () => {
    const items = Array.from({ length: 51 }, (_, i) => ({
      text: `item ${i}`,
      namespace: "ns",
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("Batch too large")
  })

  it("returns 400 when an item has invalid text type", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({
        items: [
          { text: "valid", namespace: "ns" },
          { text: 123, namespace: "ns" },
        ],
      }),
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("index 1")
  })

  it("returns 400 when an item has missing namespace", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({
        items: [{ text: "hello" }],
      }),
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toContain("index 0")
  })

  // --- Successful batch processing ---

  it("processes a single item batch successfully", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({
        items: [{ text: "Bitcoin exchange hack", namespace: "attacks" }],
      }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results).toHaveLength(1)
    expect(body.results[0]).toHaveProperty("similarity_score")
    expect(typeof body.results[0].similarity_score).toBe("number")
  })

  it("processes multiple items concurrently", async () => {
    const items = [
      { text: "Flash loan attack on DeFi protocol", namespace: "attacks" },
      { text: "Rug pull on a memecoin project", namespace: "scams" },
      { text: "Oracle manipulation vulnerability", namespace: "defi" },
    ]
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results).toHaveLength(3)
    for (const result of body.results) {
      expect(result).toHaveProperty("similarity_score")
      expect(typeof result.similarity_score).toBe("number")
    }
  })

  it("preserves optional id field in results", async () => {
    const items = [
      { id: "msg-001", text: "Test message one", namespace: "test" },
      { id: "msg-002", text: "Test message two", namespace: "test" },
    ]
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results[0].id).toBe("msg-001")
    expect(body.results[1].id).toBe("msg-002")
  })

  it("omits id field when not provided in input", async () => {
    const items = [{ text: "No ID provided", namespace: "test" }]
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results[0]).not.toHaveProperty("id")
    expect(body.results[0]).toHaveProperty("similarity_score")
  })

  // --- Response format ---

  it("returns application/json content type for batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({
        items: [{ text: "test", namespace: "ns" }],
      }),
    })
    expect(response.headers.get("content-type")).toContain("application/json")
  })

  it("returns results in the same order as input items", async () => {
    const items = Array.from({ length: 5 }, (_, i) => ({
      id: `order-${i}`,
      text: `Message number ${i}`,
      namespace: "ordering-test",
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results).toHaveLength(5)
    for (let i = 0; i < 5; i++) {
      expect(body.results[i].id).toBe(`order-${i}`)
    }
  })

  // --- Mixed namespaces ---

  it("handles items with different namespaces in one batch", async () => {
    const items = [
      { text: "Exchange security breach", namespace: "attacks" },
      { text: "New token launch", namespace: "general" },
      { text: "DeFi yield farming", namespace: "defi" },
    ]
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results).toHaveLength(3)
    for (const result of body.results) {
      expect(typeof result.similarity_score).toBe("number")
    }
  })

  // --- Edge cases ---

  it("handles batch at maximum allowed size", async () => {
    const items = Array.from({ length: 50 }, (_, i) => ({
      text: `Max batch item ${i}`,
      namespace: "stress",
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ items }),
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ results: any[] }>()
    expect(body.results).toHaveLength(50)
  })
})
