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

describe("Single text endpoint", () => {
  it("returns similarity_score for valid input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as any
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

describe("Batch endpoint", () => {
  it("returns per-text results for texts array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        namespace: "test-namespace",
        texts: ["first text", "second text"]
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as any
    expect(json.namespace).toBe("test-namespace")
    expect(json.topK).toBe(1)
    expect(Array.isArray(json.results)).toBe(true)
    expect(json.results).toHaveLength(2)
    expect(json.results[0].index).toBe(0)
    expect(json.results[0].text).toBe("first text")
    expect(typeof json.results[0].similarity_score).toBe("number")
    expect(json.results[1].index).toBe(1)
    expect(json.results[1].text).toBe("second text")
  })

  it("supports entries array shape", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        namespace: "test-namespace",
        entries: [{ text: "hello" }, { text: "world" }],
        topK: 2
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as any
    expect(json.topK).toBe(2)
    expect(json.results).toHaveLength(2)
  })

  it("handles empty batch", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        namespace: "test-namespace",
        texts: []
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json() as any
    expect(json.results).toEqual([])
  })

  it("rejects batch with non-string elements", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        namespace: "test-namespace",
        texts: ["valid", 123]
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("rejects batch exceeding max size", async () => {
    const texts = Array.from({ length: 51 }, (_, i) => `text-${i}`)
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({
        namespace: "test-namespace",
        texts
      })
    })

    expect(response.status).toBe(413)
    expect(await response.text()).toBe("Batch size too large")
  })

  it("requires authentication", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        namespace: "test-namespace",
        texts: ["hello"]
      })
    })

    expect(response.status).toBe(401)
  })
})
