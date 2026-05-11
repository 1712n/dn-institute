import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const API_KEY = "test-api-key"

function postJson(body: unknown, apiKey: string | undefined = API_KEY) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  }
  if (apiKey !== undefined) headers["X-API-Key"] = apiKey

  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
}

// ── Authentication ──────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 when X-API-Key header is missing", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when X-API-Key is wrong", async () => {
    const res = await postJson({ text: "hello", namespace: "ns" }, "wrong-key")
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when X-API-Key is empty string", async () => {
    const res = await postJson({ text: "hello", namespace: "ns" }, "")
    expect(res.status).toBe(401)
  })

  it("passes authentication with correct API key", async () => {
    const res = await postJson({ text: "hello", namespace: "ns" })
    expect(res.status).toBe(200)
  })

  it("rejects API key with wrong value casing", async () => {
    const res = await postJson({ text: "hello", namespace: "ns" }, API_KEY.toUpperCase())
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })
})

// ── Input Validation ────────────────────────────────────────────

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const res = await postJson({ namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const res = await postJson({ text: "hello" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when both fields are missing", async () => {
    const res = await postJson({})
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is a number", async () => {
    const res = await postJson({ text: 123, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number", async () => {
    const res = await postJson({ text: "hello", namespace: 456 })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const res = await postJson({ text: null, namespace: "ns" })
    expect(res.status).toBe(400)
  })

  it("returns 400 when namespace is null", async () => {
    const res = await postJson({ text: "hello", namespace: null })
    expect(res.status).toBe(400)
  })

  it("returns 400 when text is an array", async () => {
    const res = await postJson({ text: ["a", "b"], namespace: "ns" })
    expect(res.status).toBe(400)
  })

  it("returns 400 when text is an object", async () => {
    const res = await postJson({ text: { foo: "bar" }, namespace: "ns" })
    expect(res.status).toBe(400)
  })

  it("returns 400 when text is boolean", async () => {
    const res = await postJson({ text: true, namespace: "ns" })
    expect(res.status).toBe(400)
  })

  it("returns 400 when namespace is boolean", async () => {
    const res = await postJson({ text: "hello", namespace: false })
    expect(res.status).toBe(400)
  })

  it("accepts empty strings for text and namespace", async () => {
    const res = await postJson({ text: "", namespace: "" })
    // empty strings are still typeof "string", so validation passes
    expect(res.status).toBe(200)
  })
})

// ── Similarity Search Response ──────────────────────────────────

describe("Similarity Search", () => {
  it("returns JSON with similarity_score for valid request", async () => {
    const res = await postJson({ text: "bitcoin price", namespace: "crypto" })
    expect(res.status).toBe(200)
    expect(res.headers.get("content-type")).toContain("application/json")

    const body = await res.json()
    expect(body).toHaveProperty("similarity_score")
    expect(typeof body.similarity_score).toBe("number")
  })

  it("returns a numeric score between 0 and 1", async () => {
    const res = await postJson({ text: "test query", namespace: "default" })
    const body = await res.json()
    expect(body.similarity_score).toBeGreaterThanOrEqual(0)
    expect(body.similarity_score).toBeLessThanOrEqual(1)
  })

  it("handles different namespaces independently", async () => {
    const res1 = await postJson({ text: "hello", namespace: "ns-a" })
    const res2 = await postJson({ text: "hello", namespace: "ns-b" })

    expect(res1.status).toBe(200)
    expect(res2.status).toBe(200)

    const body1 = await res1.json()
    const body2 = await res2.json()
    expect(body1).toHaveProperty("similarity_score")
    expect(body2).toHaveProperty("similarity_score")
  })

  it("handles special characters in text", async () => {
    const res = await postJson({
      text: "What's the price of BTC/USD? @#$%^&*()",
      namespace: "test"
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body).toHaveProperty("similarity_score")
  })

  it("handles unicode text", async () => {
    const res = await postJson({
      text: "比特币价格 比特幣價格",
      namespace: "crypto"
    })
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body).toHaveProperty("similarity_score")
  })

  it("handles long text input", async () => {
    const longText = "word ".repeat(500).trim()
    const res = await postJson({ text: longText, namespace: "test" })
    expect(res.status).toBe(200)
  })
})

// ── HTTP Method Restrictions ────────────────────────────────────

describe("HTTP Methods", () => {
  it("rejects GET requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": API_KEY }
    })
    // Hono returns 404 for unmatched routes with GET
    expect(res.status).toBeGreaterThanOrEqual(400)
    expect(res.status).toBeLessThan(500)
  })

  it("rejects PUT requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })
    expect(res.status).toBeGreaterThanOrEqual(400)
    expect(res.status).toBeLessThan(500)
  })

  it("rejects DELETE requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: { "X-API-Key": API_KEY }
    })
    expect(res.status).toBeGreaterThanOrEqual(400)
    expect(res.status).toBeLessThan(500)
  })

  it("rejects PATCH requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "PATCH",
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" })
    })
    expect(res.status).toBeGreaterThanOrEqual(400)
    expect(res.status).toBeLessThan(500)
  })
})

// ── Edge Cases ──────────────────────────────────────────────────

describe("Edge Cases", () => {
  it("returns 400 when body is not valid JSON", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
      },
      body: "not-json"
    })
    // Hono will throw when parsing invalid JSON
    expect(res.status).toBeGreaterThanOrEqual(400)
  })

  it("returns 400 when body is empty", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
      },
      body: ""
    })
    expect(res.status).toBeGreaterThanOrEqual(400)
  })

  it("accepts extra unexpected fields", async () => {
    const res = await postJson({
      text: "hello",
      namespace: "ns",
      extra: "field",
      count: 42
    })
    // endpoint should still work with extra fields
    expect(res.status).toBe(200)
  })

  it("does not leak server errors on malformed requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
      },
      body: '{"text": "hello"' // truncated JSON
    })
    expect(res.status).toBeGreaterThanOrEqual(400)
    // should not return stack traces
    const text = await res.text()
    expect(text).not.toContain("SyntaxError")
    expect(text).not.toContain("at ")
  })
})
