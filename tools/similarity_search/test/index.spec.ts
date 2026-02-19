import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// 🌰 Shared helpers
const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

const NO_AUTH_HEADERS = {
  "Content-Type": "application/json"
}

function postRequest(
  body: unknown,
  headers: Record<string, string> = VALID_HEADERS,
  path = "/"
) {
  return SELF.fetch(`https://example.com${path}`, {
    method: "POST",
    headers,
    body: typeof body === "string" ? body : JSON.stringify(body)
  })
}

// 🌰 Authentication middleware tests
describe("🌰 Authentication", () => {
  it("returns 401 when X-API-Key header is missing", async () => {
    const res = await postRequest(
      { text: "hello", namespace: "test" },
      NO_AUTH_HEADERS
    )
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when X-API-Key is incorrect", async () => {
    const res = await postRequest(
      { text: "hello", namespace: "test" },
      { "Content-Type": "application/json", "X-API-Key": "wrong-key" }
    )
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when X-API-Key is empty string", async () => {
    const res = await postRequest(
      { text: "hello", namespace: "test" },
      { "Content-Type": "application/json", "X-API-Key": "" }
    )
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("blocks unauthenticated requests regardless of path", async () => {
    const res = await SELF.fetch("https://example.com/nonexistent", {
      method: "POST",
      headers: NO_AUTH_HEADERS,
      body: JSON.stringify({ text: "hello", namespace: "test" })
    })
    expect(res.status).toBe(401)
  })
})

// 🌰 POST / — happy path
describe("🌰 POST / — happy path", () => {
  it("returns similarity score for valid input", async () => {
    const res = await postRequest({ text: "sample text", namespace: "test-ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns the mocked similarity score (0.5678)", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    const json = (await res.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeCloseTo(0.5678, 4)
  })

  it("responds with application/json content type", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    expect(res.headers.get("content-type")).toContain("application/json")
  })

  it("returns only similarity_score in response body", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    const json = (await res.json()) as Record<string, unknown>
    expect(Object.keys(json)).toEqual(["similarity_score"])
  })
})

// 🌰 POST / — input validation
describe("🌰 POST / — input validation", () => {
  it("returns 400 when text is a number", async () => {
    const res = await postRequest({ text: 123, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number", async () => {
    const res = await postRequest({ text: "hello", namespace: 456 })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const res = await postRequest({ text: null, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is null", async () => {
    const res = await postRequest({ text: "hello", namespace: null })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text field is missing", async () => {
    const res = await postRequest({ namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const res = await postRequest({ text: "hello" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is boolean", async () => {
    const res = await postRequest({ text: true, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is an array", async () => {
    const res = await postRequest({ text: ["a", "b"], namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 500 when body is malformed JSON (unhandled parse error)", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: "not-json{{"
    })
    expect(res.status).toBe(500)
  })

  it("returns 500 when body is empty (unhandled parse error)", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: VALID_HEADERS,
      body: ""
    })
    expect(res.status).toBe(500)
  })
})

// 🌰 POST / — edge cases
describe("🌰 POST / — edge cases", () => {
  it("handles empty string text and namespace", async () => {
    const res = await postRequest({ text: "", namespace: "" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles very long text input (10k characters)", async () => {
    const longText = "a".repeat(10_000)
    const res = await postRequest({ text: longText, namespace: "ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles unicode text", async () => {
    const res = await postRequest({
      text: "你好世界 🌰 مرحبا العالم こんにちは",
      namespace: "unicode-ns"
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles special characters and XSS payloads safely", async () => {
    const res = await postRequest({
      text: '<script>alert("xss")</script>',
      namespace: "security"
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles unicode namespace", async () => {
    const res = await postRequest({
      text: "test",
      namespace: "名前空間-🌰"
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("ignores extra fields in request body", async () => {
    const res = await postRequest({
      text: "test",
      namespace: "ns",
      extra: "should-be-ignored",
      another: 42
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("returns score 0 when no vectorize matches found", async () => {
    const res = await postRequest({ text: "no match", namespace: "empty-ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0)
  })

  it("similarity score is within valid range [0, 1]", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    const json = (await res.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })
})

// 🌰 HTTP method handling
describe("🌰 HTTP method handling", () => {
  it("returns 404 for GET request", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: VALID_HEADERS
    })
    expect(res.status).toBe(404)
  })

  it("returns 404 for PUT request", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })
    expect(res.status).toBe(404)
  })

  it("returns 404 for DELETE request", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: VALID_HEADERS
    })
    expect(res.status).toBe(404)
  })

  it("returns 404 for undefined routes", async () => {
    const res = await postRequest(
      { text: "test", namespace: "ns" },
      VALID_HEADERS,
      "/nonexistent"
    )
    expect(res.status).toBe(404)
  })
})

// 🌰 Response structure validation
describe("🌰 Response structure", () => {
  it("successful response is valid JSON", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    const text = await res.text()
    expect(() => JSON.parse(text)).not.toThrow()
  })

  it("error responses are plain text, not JSON", async () => {
    const res = await postRequest({ text: 123, namespace: "ns" })
    expect(res.status).toBe(400)
    const text = await res.text()
    expect(text).toBe("Invalid JSON format")
    expect(res.headers.get("content-type")).toContain("text/plain")
  })

  it("401 response body is plain text", async () => {
    const res = await postRequest(
      { text: "test", namespace: "ns" },
      NO_AUTH_HEADERS
    )
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
    expect(res.headers.get("content-type")).toContain("text/plain")
  })
})
