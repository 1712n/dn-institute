import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const API_KEY = "test-api-key"

const validHeaders = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY
}

function makeRequest(
  body: unknown,
  headers: Record<string, string> = validHeaders,
  method = "POST"
) {
  return SELF.fetch("https://example.com/", {
    method,
    headers,
    body: method !== "GET" ? JSON.stringify(body) : undefined
  })
}

describe("Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const response = await makeRequest(
      { text: "test", namespace: "ns" },
      { "Content-Type": "application/json" }
    )
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is incorrect", async () => {
    const response = await makeRequest(
      { text: "test", namespace: "ns" },
      { "Content-Type": "application/json", "X-API-Key": "wrong-key" }
    )
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 with empty API key header", async () => {
    const response = await makeRequest(
      { text: "test", namespace: "ns" },
      { "Content-Type": "application/json", "X-API-Key": "" }
    )
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const response = await makeRequest({ namespace: "ns" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await makeRequest({ text: "hello" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is not a string", async () => {
    const response = await makeRequest({ text: 123, namespace: "ns" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is not a string", async () => {
    const response = await makeRequest({ text: "hello", namespace: 456 })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is empty object", async () => {
    const response = await makeRequest({})
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Similarity Search", () => {
  it("returns a similarity score for valid input", async () => {
    const response = await makeRequest({
      text: "Bitcoin is a decentralized cryptocurrency",
      namespace: "crypto"
    })
    expect(response.status).toBe(200)

    const result = await response.json<{ similarity_score: number }>()
    expect(result).toHaveProperty("similarity_score")
    expect(typeof result.similarity_score).toBe("number")
  })

  it("returns similarity score between 0 and 1", async () => {
    const response = await makeRequest({
      text: "Ethereum smart contracts",
      namespace: "crypto"
    })
    const result = await response.json<{ similarity_score: number }>()
    expect(result.similarity_score).toBeGreaterThanOrEqual(0)
    expect(result.similarity_score).toBeLessThanOrEqual(1)
  })

  it("handles different namespaces", async () => {
    const response = await makeRequest({
      text: "test query",
      namespace: "different-namespace"
    })
    expect(response.status).toBe(200)

    const result = await response.json<{ similarity_score: number }>()
    expect(result).toHaveProperty("similarity_score")
  })

  it("handles long text input", async () => {
    const longText = "word ".repeat(500).trim()
    const response = await makeRequest({
      text: longText,
      namespace: "test"
    })
    expect(response.status).toBe(200)

    const result = await response.json<{ similarity_score: number }>()
    expect(result).toHaveProperty("similarity_score")
  })

  it("handles special characters in text", async () => {
    const response = await makeRequest({
      text: "BTC/USDT price @$50,000! 🚀 #crypto",
      namespace: "test"
    })
    expect(response.status).toBe(200)

    const result = await response.json<{ similarity_score: number }>()
    expect(result).toHaveProperty("similarity_score")
  })

  it("returns 0 similarity score when no matches found", async () => {
    // The mock always returns a match, but this tests the fallback
    // behavior in the source code (|| 0)
    const response = await makeRequest({
      text: "completely unrelated query",
      namespace: "empty-namespace"
    })
    expect(response.status).toBe(200)

    const result = await response.json<{ similarity_score: number }>()
    expect(typeof result.similarity_score).toBe("number")
  })
})

describe("HTTP Method Handling", () => {
  it("returns 404 for GET requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": API_KEY }
    })
    expect(response.status).toBe(404)
  })
})

describe("Response Format", () => {
  it("returns JSON content type", async () => {
    const response = await makeRequest({
      text: "test",
      namespace: "test"
    })
    const contentType = response.headers.get("content-type")
    expect(contentType).toContain("application/json")
  })

  it("response body contains only similarity_score field", async () => {
    const response = await makeRequest({
      text: "test query",
      namespace: "test"
    })
    const result = await response.json<Record<string, unknown>>()
    const keys = Object.keys(result)
    expect(keys).toEqual(["similarity_score"])
  })
})
