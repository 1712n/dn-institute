import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_API_KEY = "test-api-key"

function makeRequest(path: string, body: unknown, apiKey?: string) {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (apiKey) headers["X-API-Key"] = apiKey
  return SELF.fetch(`https://example.com${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
}

// ── Authentication ──────────────────────────────────────────────────

describe("Authentication", () => {
  it("rejects requests without an API key", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "ns" })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("rejects requests with an incorrect API key", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "ns" }, "wrong-key")
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("accepts requests with the correct API key", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "ns" }, VALID_API_KEY)
    expect(res.status).toBe(200)
  })

  it("applies authentication to all routes", async () => {
    const paths = ["/", "/nonexistent"]
    for (const path of paths) {
      const res = await makeRequest(path, { text: "hello", namespace: "ns" })
      expect(res.status).toBe(401)
    }
  })
})

// ── POST / — Single message similarity search ──────────────────────

describe("POST / — Single message", () => {
  it("returns a similarity score for valid input", async () => {
    const res = await makeRequest("/", { text: "test message", namespace: "wiki" }, VALID_API_KEY)
    expect(res.status).toBe(200)

    const json = await res.json() as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns application/json content type", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "ns" }, VALID_API_KEY)
    expect(res.headers.get("content-type")).toContain("application/json")
  })

  it("rejects non-string text field", async () => {
    const res = await makeRequest("/", { text: 42, namespace: "ns" }, VALID_API_KEY)
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("rejects non-string namespace field", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: 123 }, VALID_API_KEY)
    expect(res.status).toBe(400)
  })

  it("rejects missing text field", async () => {
    const res = await makeRequest("/", { namespace: "ns" }, VALID_API_KEY)
    expect(res.status).toBe(400)
  })

  it("rejects missing namespace field", async () => {
    const res = await makeRequest("/", { text: "hello" }, VALID_API_KEY)
    expect(res.status).toBe(400)
  })

  it("rejects empty object body", async () => {
    const res = await makeRequest("/", {}, VALID_API_KEY)
    expect(res.status).toBe(400)
  })

  it("handles unicode text", async () => {
    const res = await makeRequest("/", { text: "日本語テスト 🔥", namespace: "ns" }, VALID_API_KEY)
    expect(res.status).toBe(200)
    const json = await res.json() as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles long text input", async () => {
    const longText = "a".repeat(10000)
    const res = await makeRequest("/", { text: longText, namespace: "ns" }, VALID_API_KEY)
    expect(res.status).toBe(200)
    const json = await res.json() as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 0 when namespace has no matches", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "empty-namespace" }, VALID_API_KEY)
    expect(res.status).toBe(200)
    const json = await res.json() as { similarity_score: number }
    expect(json.similarity_score).toBe(0)
  })
})

// ── HTTP method handling ────────────────────────────────────────────

describe("HTTP method handling", () => {
  it("rejects GET requests to /", async () => {
    const res = await SELF.fetch("https://example.com/", {
      headers: { "X-API-Key": VALID_API_KEY }
    })
    // Hono returns 404 for unmatched routes/methods
    expect(res.status).toBe(404)
  })

  it("rejects PUT requests to /", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": VALID_API_KEY
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })
    expect(res.status).toBe(404)
  })

  it("rejects DELETE requests to /", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: { "X-API-Key": VALID_API_KEY }
    })
    expect(res.status).toBe(404)
  })
})

// ── Response structure ──────────────────────────────────────────────

describe("Response structure", () => {
  it("returns only the expected fields in single-message response", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "ns" }, VALID_API_KEY)
    const json = await res.json() as Record<string, unknown>
    const keys = Object.keys(json)
    expect(keys).toEqual(["similarity_score"])
  })

  it("returns numeric similarity_score between 0 and 1", async () => {
    const res = await makeRequest("/", { text: "hello", namespace: "ns" }, VALID_API_KEY)
    const json = await res.json() as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })
})

// ── Concurrent requests ─────────────────────────────────────────────

describe("Concurrent requests", () => {
  it("handles multiple simultaneous requests", async () => {
    const requests = Array.from({ length: 5 }, (_, i) =>
      makeRequest("/", { text: `message ${i}`, namespace: "ns" }, VALID_API_KEY)
    )
    const responses = await Promise.all(requests)

    for (const res of responses) {
      expect(res.status).toBe(200)
      const json = await res.json() as { similarity_score: number }
      expect(json).toHaveProperty("similarity_score")
    }
  })

  it("isolates authentication failures from successful requests", async () => {
    const [authFail, success] = await Promise.all([
      makeRequest("/", { text: "hello", namespace: "ns" }),
      makeRequest("/", { text: "hello", namespace: "ns" }, VALID_API_KEY)
    ])

    expect(authFail.status).toBe(401)
    expect(success.status).toBe(200)
  })
})

// ── Unmatched routes ────────────────────────────────────────────────

describe("Unmatched routes", () => {
  it("returns 404 for unknown paths", async () => {
    const res = await SELF.fetch("https://example.com/unknown/path", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": VALID_API_KEY
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })
    expect(res.status).toBe(404)
  })
})
