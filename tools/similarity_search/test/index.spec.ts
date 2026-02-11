import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_API_KEY = "test-api-key"

function makeHeaders(apiKey?: string): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (apiKey) {
    headers["X-API-Key"] = apiKey
  }
  return headers
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(),
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 Unauthorized when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders("wrong-key"),
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Single message endpoint: POST /", () => {
  it("returns 400 for invalid JSON format", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ text: 123, namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ text: "hello" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Batch endpoint: POST /batch", () => {
  it("returns 401 Unauthorized without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(),
      body: JSON.stringify({ messages: [{ text: "hello", namespace: "test" }] })
    })

    expect(response.status).toBe(401)
  })

  it("returns 400 for empty messages array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ messages: [] })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty")
  })

  it("returns 400 when messages is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ messages: "not-an-array" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty")
  })

  it("returns 400 when batch size exceeds maximum", async () => {
    const messages = Array.from({ length: 49 }, (_, i) => ({
      text: `message ${i}`,
      namespace: "test"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({ messages })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("exceeds maximum")
  })

  it("returns 400 when a message has invalid format", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: makeHeaders(VALID_API_KEY),
      body: JSON.stringify({
        messages: [
          { text: "valid", namespace: "test" },
          { text: 123, namespace: "test" }
        ]
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("each message")
  })
})
