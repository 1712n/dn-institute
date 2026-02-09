import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key",
}

function validBody(overrides?: Record<string, unknown>) {
  return JSON.stringify({ text: "sample text", namespace: "test-ns", ...overrides })
}

describe("Authentication", () => {
  it.each([
    { case: "missing", headers: { "Content-Type": "application/json" } },
    { case: "invalid", headers: { "Content-Type": "application/json", "X-API-Key": "wrong-key" } },
  ])("returns 401 when API key is $case", async ({ headers }) => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers,
      body: validBody(),
    })
    expect(response.status).toBe(401)
  })

  it("accepts requests with a valid API key", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: validBody(),
    })
    expect(response.status).toBe(200)
  })
})

describe("Input Validation", () => {
  it.each([
    { case: "text is missing", body: { namespace: "ns" } },
    { case: "namespace is missing", body: { text: "hello" } },
    { case: "text is not a string", body: { text: 123, namespace: "ns" } },
    { case: "namespace is not a string", body: { text: "hello", namespace: 42 } },
    { case: "both fields are missing", body: {} },
  ])("returns 400 when $case", async ({ body }) => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify(body),
    })
    expect(response.status).toBe(400)
  })
})

describe("Routing", () => {
  it("returns 404 for unregistered paths", async () => {
    const response = await SELF.fetch("https://example.com/nonexistent", {
      method: "POST",
      headers: VALID_HEADERS,
      body: validBody(),
    })
    expect(response.status).toBe(404)
  })

  it("returns 404 for non-POST methods on /", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: VALID_HEADERS,
    })
    expect(response.status).toBe(404)
  })
})

describe("Similarity Search", () => {
  it("returns 200 with a similarity_score for valid input", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: validBody(),
    })
    expect(response.status).toBe(200)
    const data = await response.json<{ similarity_score: number }>()
    expect(data).toHaveProperty("similarity_score")
    expect(typeof data.similarity_score).toBe("number")
  })

  it("returns the score produced by the Vectorize index", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: validBody(),
    })
    const data = await response.json<{ similarity_score: number }>()
    expect(data.similarity_score).toBe(0.5678)
  })

  it("processes different text inputs without error", async () => {
    const inputs = [
      { text: "short", namespace: "ns" },
      { text: "a longer piece of text that contains multiple words and phrases", namespace: "articles" },
      { text: "Unicode: Ünîcödé テスト 你好", namespace: "multilingual" },
    ]

    for (const body of inputs) {
      const response = await SELF.fetch("https://example.com/", {
        method: "POST",
        headers: VALID_HEADERS,
        body: JSON.stringify(body),
      })
      expect(response.status).toBe(200)
      const data = await response.json<{ similarity_score: number }>()
      expect(typeof data.similarity_score).toBe("number")
    }
  })

  it("returns JSON content type", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: validBody(),
    })
    expect(response.headers.get("content-type")).toContain("application/json")
  })
})
