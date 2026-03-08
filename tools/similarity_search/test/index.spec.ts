import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const API_KEY = "test-api-key"

/**
 * Helper to make authenticated POST requests to the similarity search API.
 */
async function postSearch(
  body: unknown,
  options?: { headers?: Record<string, string>; rawBody?: string }
) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    ...options?.headers
  }

  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers,
    body: options?.rawBody ?? JSON.stringify(body)
  })
}

// ─── Authentication ──────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is incorrect", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("passes authentication with the correct API key", async () => {
    const response = await postSearch({ text: "hello", namespace: "ns" })

    // Should not be 401 – the request reaches the handler
    expect(response.status).not.toBe(401)
  })
})

// ─── Input Validation ────────────────────────────────────────────

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const response = await postSearch({ namespace: "ns" })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await postSearch({ text: "hello" })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 for invalid (non-JSON) request body", async () => {
    const response = await postSearch(null, {
      rawBody: "this is not json"
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when text is a number instead of string", async () => {
    const response = await postSearch({ text: 123, namespace: "ns" })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number instead of string", async () => {
    const response = await postSearch({ text: "hello", namespace: 456 })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const response = await postSearch({ text: null, namespace: "ns" })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when both fields are arrays", async () => {
    const response = await postSearch({ text: ["a"], namespace: ["b"] })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

// ─── Similarity Search (core functionality) ──────────────────────

describe("Similarity Search", () => {
  it("returns a JSON response with similarity_score for valid input", async () => {
    const response = await postSearch({
      text: "Bitcoin price manipulation",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns similarity_score between 0 and 1", async () => {
    const response = await postSearch({
      text: "Ethereum smart contracts",
      namespace: "test-namespace"
    })

    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns the expected mock score (0.5678)", async () => {
    // The miniflare mock vectorize-index always returns score 0.5678
    const response = await postSearch({
      text: "Test query",
      namespace: "any-namespace"
    })

    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("handles empty string text gracefully", async () => {
    const response = await postSearch({ text: "", namespace: "ns" })

    // Empty string is still a valid string type, so the handler should process it
    // The mock will return a score regardless
    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles empty string namespace gracefully", async () => {
    const response = await postSearch({ text: "hello", namespace: "" })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })
})

// ─── Edge Cases ──────────────────────────────────────────────────

describe("Edge Cases", () => {
  it("handles very long text input", async () => {
    const longText = "a".repeat(10_000)
    const response = await postSearch({
      text: longText,
      namespace: "ns"
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles special characters and unicode", async () => {
    const response = await postSearch({
      text: "特殊字符 🚀 émojis & <script>alert('xss')</script>",
      namespace: "test-ns"
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles namespace with special characters", async () => {
    const response = await postSearch({
      text: "test",
      namespace: "ns/with-special_chars.v2"
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles concurrent requests without errors", async () => {
    const requests = Array.from({ length: 10 }, (_, i) =>
      postSearch({
        text: `concurrent request ${i}`,
        namespace: "test-namespace"
      })
    )

    const responses = await Promise.all(requests)

    for (const response of responses) {
      expect(response.status).toBe(200)

      const json = (await response.json()) as { similarity_score: number }
      expect(json).toHaveProperty("similarity_score")
      expect(json.similarity_score).toBe(0.5678)
    }
  })

  it("rejects requests with unsupported HTTP methods", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": API_KEY }
    })

    // Hono returns 404 for unmatched routes
    expect(response.status).toBe(404)
  })

  it("returns Content-Type application/json for successful responses", async () => {
    const response = await postSearch({
      text: "content type check",
      namespace: "ns"
    })

    expect(response.status).toBe(200)
    expect(response.headers.get("Content-Type")).toContain("application/json")
  })

  it("handles additional unexpected fields in the body gracefully", async () => {
    const response = await postSearch({
      text: "hello",
      namespace: "ns",
      extra_field: "should be ignored"
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })
})
