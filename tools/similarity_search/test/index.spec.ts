import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// Helper to build a valid authenticated request
function buildRequest(
  body: unknown,
  options: { apiKey?: string; method?: string; contentType?: string } = {}
) {
  const { apiKey = "test-api-key", method = "POST", contentType = "application/json" } = options
  const headers: Record<string, string> = {}
  if (apiKey) headers["X-API-Key"] = apiKey
  if (contentType) headers["Content-Type"] = contentType

  const init: RequestInit = { method, headers }
  if (method !== "GET" && method !== "HEAD" && body !== undefined) {
    init.body = typeof body === "string" ? body : JSON.stringify(body)
  }
  return init
}

describe("Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is incorrect", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "test", namespace: "ns" }, { apiKey: "wrong-key" })
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is empty string", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": ""
      },
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("accepts request with valid API key", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "Hello world", namespace: "test-ns" })
    )

    expect(response.status).toBe(200)
  })
})

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ namespace: "test-ns" })
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "Hello" })
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is a number instead of string", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: 12345, namespace: "ns" })
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number instead of string", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "hello", namespace: 42 })
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: null, namespace: "ns" })
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is an empty object", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({})
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is an array", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: ["a", "b"], namespace: "ns" })
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Similarity Search Endpoint", () => {
  it("returns a similarity score for a valid request", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "Bitcoin price prediction", namespace: "crypto" })
    )

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
    // The mock vectorize returns 0.5678
    expect(json.similarity_score).toBe(0.5678)
  })

  it("returns similarity score as a number between 0 and 1", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "Ethereum smart contracts", namespace: "crypto" })
    )

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns JSON content type", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "test query", namespace: "default" })
    )

    expect(response.status).toBe(200)
    expect(response.headers.get("content-type")).toContain("application/json")
  })

  it("handles empty string text input", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "", namespace: "test" })
    )

    // Empty string is still a valid string type, so the worker should process it
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles long text input", async () => {
    const longText = "A".repeat(10000)
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: longText, namespace: "test" })
    )

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles special characters in text and namespace", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({
        text: "Test with special chars: <>&\"'!@#$%^*()",
        namespace: "ns-with-special_chars.v2"
      })
    )

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles unicode text input", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({
        text: "比特币价格预测 🚀 données cryptographiques",
        namespace: "multilingual"
      })
    )

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })
})

describe("HTTP Method Handling", () => {
  it("returns 404 for GET requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": "test-api-key" }
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for PUT requests", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "test", namespace: "ns" }, { method: "PUT" })
    )

    expect(response.status).toBe(404)
  })

  it("returns 404 for DELETE requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: { "X-API-Key": "test-api-key" }
    })

    expect(response.status).toBe(404)
  })
})

describe("Route Handling", () => {
  it("returns 404 for non-root paths", async () => {
    const response = await SELF.fetch(
      "https://example.com/nonexistent",
      buildRequest({ text: "test", namespace: "ns" })
    )

    expect(response.status).toBe(404)
  })

  it("returns 404 for nested paths", async () => {
    const response = await SELF.fetch(
      "https://example.com/api/search",
      buildRequest({ text: "test", namespace: "ns" })
    )

    expect(response.status).toBe(404)
  })
})

describe("Response Structure", () => {
  it("returns only the similarity_score field in response", async () => {
    const response = await SELF.fetch(
      "https://example.com/",
      buildRequest({ text: "check response structure", namespace: "test" })
    )

    expect(response.status).toBe(200)
    const json = (await response.json()) as Record<string, unknown>
    const keys = Object.keys(json)
    expect(keys).toEqual(["similarity_score"])
  })

  it("returns consistent results for identical requests", async () => {
    const body = { text: "consistent test", namespace: "test" }

    const response1 = await SELF.fetch("https://example.com/", buildRequest(body))
    const response2 = await SELF.fetch("https://example.com/", buildRequest(body))

    const json1 = (await response1.json()) as { similarity_score: number }
    const json2 = (await response2.json()) as { similarity_score: number }

    expect(json1.similarity_score).toBe(json2.similarity_score)
  })
})
