/**
 * 🌰 Similarity Search API — Integration Tests 🌰
 *
 * Comprehensive integration test suite for the Similarity Search worker.
 * Tests higher-level API functionality including authentication,
 * request validation, similarity scoring, and error handling.
 *
 * Uses Cloudflare Vitest integration with miniflare bindings
 * for realistic worker environment simulation. 🌰
 */
import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// 🌰 Helper: make an authenticated POST request
async function authenticatedPost(
  body: unknown,
  headers: Record<string, string> = {}
) {
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "test-api-key",
      ...headers,
    },
    body: JSON.stringify(body),
  })
}

// 🌰 Helper: make an unauthenticated POST request
async function unauthenticatedPost(
  body: unknown,
  headers: Record<string, string> = {}
) {
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(body),
  })
}

/**
 * 🌰 Authentication Tests 🌰
 * Verify the API key middleware correctly gates all requests.
 */
describe("🌰 Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const response = await unauthenticatedPost({
      text: "Sample text",
      namespace: "test-namespace",
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is incorrect", async () => {
    const response = await unauthenticatedPost(
      { text: "Sample text", namespace: "test-namespace" },
      { "X-API-Key": "wrong-key-value" }
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is empty string", async () => {
    const response = await unauthenticatedPost(
      { text: "Sample text", namespace: "test-namespace" },
      { "X-API-Key": "" }
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("accepts valid API key and processes request", async () => {
    const response = await authenticatedPost({
      text: "Valid text input",
      namespace: "test-namespace",
    })

    // Should not be 401 — auth passed
    expect(response.status).not.toBe(401)
  })
})

/**
 * 🌰 Request Validation Tests 🌰
 * Verify the worker correctly validates incoming JSON payloads.
 */
describe("🌰 Request Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const response = await authenticatedPost({
      namespace: "test-namespace",
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await authenticatedPost({
      text: "Some text here",
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is not a string (number)", async () => {
    const response = await authenticatedPost({
      text: 12345,
      namespace: "test-namespace",
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is not a string (boolean)", async () => {
    const response = await authenticatedPost({
      text: "Valid text",
      namespace: true,
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const response = await authenticatedPost({
      text: null,
      namespace: "test-namespace",
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is an array", async () => {
    const response = await authenticatedPost({
      text: "Some text",
      namespace: ["invalid"],
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is empty object", async () => {
    const response = await authenticatedPost({})

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

/**
 * 🌰 Similarity Scoring Tests 🌰
 * Verify the end-to-end similarity search pipeline:
 * text → AI embedding → Vectorize query → similarity score response.
 */
describe("🌰 Similarity Scoring", () => {
  it("returns JSON response with similarity_score field", async () => {
    const response = await authenticatedPost({
      text: "Test text for similarity",
      namespace: "test-namespace",
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("returns similarity_score as a number", async () => {
    const response = await authenticatedPost({
      text: "Another test text",
      namespace: "test-namespace",
    })

    const json = (await response.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns similarity_score from mock Vectorize (0.5678)", async () => {
    const response = await authenticatedPost({
      text: "Check similarity score value",
      namespace: "test-namespace",
    })

    const json = (await response.json()) as { similarity_score: number }
    // Our mock Vectorize returns 0.5678
    expect(json.similarity_score).toBe(0.5678)
  })

  it("returns similarity_score between 0 and 1 (inclusive)", async () => {
    const response = await authenticatedPost({
      text: "Score range validation",
      namespace: "production",
    })

    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("processes requests with different namespaces", async () => {
    const namespaces = ["crypto-fraud", "market-manipulation", "ponzi-schemes"]

    for (const namespace of namespaces) {
      const response = await authenticatedPost({
        text: "Test across namespaces",
        namespace,
      })

      expect(response.status).toBe(200)
      const json = (await response.json()) as { similarity_score: number }
      expect(json).toHaveProperty("similarity_score")
    }
  })

  it("handles long text input gracefully", async () => {
    const longText = "A".repeat(10000)
    const response = await authenticatedPost({
      text: longText,
      namespace: "test-namespace",
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles unicode and special characters in text", async () => {
    const response = await authenticatedPost({
      text: "Bitcoin 🌰 价格 análisis données üntersuchung 🚀",
      namespace: "test-namespace",
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles empty string text (valid string type)", async () => {
    const response = await authenticatedPost({
      text: "",
      namespace: "test-namespace",
    })

    // Empty string is still typeof "string", so validation passes
    // The AI model/vectorize should handle it
    expect(response.status).toBe(200)
  })
})

/**
 * 🌰 HTTP Method Tests 🌰
 * Verify only POST is accepted at the root endpoint.
 */
describe("🌰 HTTP Methods", () => {
  it("returns 404 for GET requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: {
        "X-API-Key": "test-api-key",
      },
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for PUT requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: "test",
        namespace: "test",
      }),
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for DELETE requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: {
        "X-API-Key": "test-api-key",
      },
    })

    expect(response.status).toBe(404)
  })
})

/**
 * 🌰 Content-Type & Response Format Tests 🌰
 * Verify proper content negotiation and response formatting.
 */
describe("🌰 Response Format", () => {
  it("returns application/json content type for valid requests", async () => {
    const response = await authenticatedPost({
      text: "Content type check",
      namespace: "test-namespace",
    })

    expect(response.headers.get("content-type")).toContain("application/json")
  })

  it("response body contains only similarity_score (no extra fields)", async () => {
    const response = await authenticatedPost({
      text: "Minimal response check",
      namespace: "test-namespace",
    })

    const json = (await response.json()) as Record<string, unknown>
    const keys = Object.keys(json)
    expect(keys).toEqual(["similarity_score"])
  })
})

/**
 * 🌰 Route Tests 🌰
 * Verify routing behavior for non-root paths.
 */
describe("🌰 Routing", () => {
  it("returns 404 for undefined routes", async () => {
    const response = await SELF.fetch("https://example.com/nonexistent", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: "test",
        namespace: "test",
      }),
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for /health endpoint (not implemented)", async () => {
    const response = await SELF.fetch("https://example.com/health", {
      method: "GET",
      headers: {
        "X-API-Key": "test-api-key",
      },
    })

    expect(response.status).toBe(404)
  })
})
