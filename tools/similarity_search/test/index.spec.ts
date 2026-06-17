import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

/**
 * Integration tests for the Similarity Search API.
 *
 * These tests exercise the full request lifecycle through the Worker
 * using SELF.fetch(), which dispatches real HTTP requests to the Worker
 * under the Cloudflare Vitest pool. AI and Vectorize bindings are
 * provided by lightweight mock workers configured in vitest.config.ts.
 */

// Shared constants --------------------------------------------------------

const API_KEY = "test-api-key"

const validHeaders = (extra: Record<string, string> = {}): Record<string, string> => ({
  "Content-Type": "application/json",
  "X-API-Key": API_KEY,
  ...extra
})

const validBody = (text = "Sample text", namespace = "test-namespace"): string =>
  JSON.stringify({ text, namespace })

// -------------------------------------------------------------------------
// 1. Authentication middleware
// -------------------------------------------------------------------------
describe("Authentication", () => {
  it("rejects requests without an API key header", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: validBody()
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("rejects requests with an incorrect API key", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
      },
      body: validBody()
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("rejects requests with an empty API key header", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": ""
      },
      body: validBody()
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("allows requests with the correct API key", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody()
    })

    // A correctly authenticated request must not receive a 401
    expect(response.status).not.toBe(401)
  })

  it("applies authentication to every route, including undefined ones", async () => {
    const response = await SELF.fetch("https://example.com/nonexistent", {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// -------------------------------------------------------------------------
// 2. POST / - Similarity search endpoint (happy path)
// -------------------------------------------------------------------------
describe("POST / - Similarity search", () => {
  it("returns a similarity score for a valid request", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody("Hello world", "articles")
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
    // The mock Vectorize worker always returns score 0.5678
    expect(json.similarity_score).toBe(0.5678)
  })

  it("returns a JSON content-type header", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody()
    })

    expect(response.status).toBe(200)
    const contentType = response.headers.get("Content-Type")
    expect(contentType).toContain("application/json")
  })

  it("returns exactly one key in the response object", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody()
    })

    const json = await response.json()
    expect(Object.keys(json as Record<string, unknown>)).toEqual(["similarity_score"])
  })

  it("accepts different namespace values", async () => {
    const namespaces = ["news", "crypto", "social-media", "alerts"]

    for (const ns of namespaces) {
      const response = await SELF.fetch("https://example.com/", {
        method: "POST",
        headers: validHeaders(),
        body: validBody("test text", ns)
      })

      expect(response.status).toBe(200)
      const json = (await response.json()) as { similarity_score: number }
      expect(json.similarity_score).toBe(0.5678)
    }
  })
})

// -------------------------------------------------------------------------
// 3. Input validation
// -------------------------------------------------------------------------
describe("Input validation", () => {
  it("returns 400 when text is a number", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: 12345, namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: "valid text", namespace: 42 })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: null, namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is null", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: "valid", namespace: null })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is a boolean", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: true, namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is an array", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: ["a", "b"], namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is an object", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: { value: "hello" }, namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when both fields have wrong types", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: 123, namespace: 456 })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text field is missing entirely", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ namespace: "test" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing entirely", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({ text: "valid text" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 for an empty JSON object", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({})
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

// -------------------------------------------------------------------------
// 4. Edge cases
// -------------------------------------------------------------------------
describe("Edge cases", () => {
  it("handles empty-string text and namespace", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody("", "")
    })

    // Empty strings pass the typeof === "string" check, so processing proceeds
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles text with HTML / script-injection characters", async () => {
    const xssText = "Hello <script>alert('xss')</script> & \"quotes\" 'single'"
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody(xssText, "test")
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("handles text with Unicode and multi-byte characters", async () => {
    const unicodeText = "Bonjour le monde! Hola mundo! \u041F\u0440\u0438\u0432\u0435\u0442 \u043C\u0438\u0440! \u4F60\u597D\u4E16\u754C\uFF01"
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody(unicodeText, "multilingual")
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("handles text with emoji characters", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody("Great news! \uD83D\uDE80\uD83C\uDF89\uD83D\uDCB0", "social")
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("handles long text input", async () => {
    const longText = "word ".repeat(5000).trim()
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody(longText, "long-text-ns")
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("handles namespace with special path-like characters", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody("test", "ns/with-special.chars_and:colons")
    })

    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("handles text containing only whitespace", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: validBody("   \t\n  ", "test")
    })

    // Whitespace-only strings are still valid strings
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })
})

// -------------------------------------------------------------------------
// 5. HTTP method handling
// -------------------------------------------------------------------------
describe("HTTP method handling", () => {
  it("returns 404 for GET requests to /", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: validHeaders()
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for PUT requests to /", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: validHeaders(),
      body: validBody()
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for DELETE requests to /", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: validHeaders()
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for PATCH requests to /", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "PATCH",
      headers: validHeaders(),
      body: validBody()
    })

    expect(response.status).toBe(404)
  })
})

// -------------------------------------------------------------------------
// 6. Undefined routes
// -------------------------------------------------------------------------
describe("Undefined routes", () => {
  it("returns 404 for POST to an unregistered path", async () => {
    const response = await SELF.fetch("https://example.com/unknown", {
      method: "POST",
      headers: validHeaders(),
      body: validBody()
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for GET to an unregistered path", async () => {
    const response = await SELF.fetch("https://example.com/health", {
      method: "GET",
      headers: validHeaders()
    })

    expect(response.status).toBe(404)
  })

  it("returns 404 for a nested unregistered path", async () => {
    const response = await SELF.fetch("https://example.com/api/v1/search", {
      method: "POST",
      headers: validHeaders(),
      body: validBody()
    })

    expect(response.status).toBe(404)
  })
})

// -------------------------------------------------------------------------
// 7. Malformed request bodies
// -------------------------------------------------------------------------
describe("Malformed request bodies", () => {
  it("returns an error for non-JSON body text", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: "this is not json"
    })

    // Hono's c.req.json() will throw; the Worker returns a non-200 status
    expect(response.status).toBeGreaterThanOrEqual(400)
  })

  it("returns an error for a completely empty body", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: ""
    })

    expect(response.status).toBeGreaterThanOrEqual(400)
  })

  it("succeeds when body contains extra unknown fields alongside valid ones", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: validHeaders(),
      body: JSON.stringify({
        text: "valid text",
        namespace: "valid-ns",
        extraField: "should be ignored"
      })
    })

    // Extra fields are simply ignored by destructuring
    expect(response.status).toBe(200)
    const json = (await response.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })
})
