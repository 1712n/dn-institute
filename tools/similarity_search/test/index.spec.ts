import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

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

describe("Similarity search", () => {
  it("returns a similarity score for a single text entry", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({ similarity_score: 0.1 })
  })

  it("rejects malformed single lookup JSON", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: "{"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 502 when the single lookup embedding response is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "invalid-embedding",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Embedding response contained invalid vector at index 0")
  })

  it("processes multiple text entries in request order", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        items: [
          { text: "First text", namespace: "articles" },
          { text: "Second text", namespace: "articles" },
          { text: "Third text", namespace: "topics" }
        ]
      })
    })

    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({
      results: [
        { similarity_score: 0.1 },
        { similarity_score: 0.2 },
        { similarity_score: 0.3 }
      ]
    })
  })

  it("rejects empty batch requests", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ items: [] })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Batch size must be between 1 and 100")
  })

  it("rejects batch requests over the maximum size", async () => {
    const items = Array.from({ length: 101 }, (_, index) => ({
      text: `Text ${index}`,
      namespace: "test-namespace"
    }))
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Batch size must be between 1 and 100")
  })

  it("rejects malformed batch JSON", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: "{"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("rejects invalid batch entries", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        items: [
          { text: "Valid text", namespace: "test-namespace" },
          { text: "", namespace: "test-namespace" }
        ]
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})
