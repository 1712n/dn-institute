import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const API_KEY = "test-api-key"

function validHeaders(overrides: Record<string, string> = {}) {
  return {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    ...overrides,
  }
}

function post(
  body: unknown,
  headers?: Record<string, string>,
  path = "/"
) {
  return SELF.fetch(`https://example.com${path}`, {
    method: "POST",
    headers: validHeaders(headers),
    body: typeof body === "string" ? body : JSON.stringify(body),
  })
}

function req(method: string, path = "/") {
  return SELF.fetch(`https://example.com${path}`, {
    method,
    headers: validHeaders(),
  })
}

describe("Authentication", () => {
  it("rejects requests without an API key header", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "hello", namespace: "test" }),
    })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("rejects requests with an incorrect API key", async () => {
    const res = await post(
      { text: "hello", namespace: "test" },
      { "X-API-Key": "wrong-key" }
    )
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("rejects requests with an empty API key header", async () => {
    const res = await post(
      { text: "hello", namespace: "test" },
      { "X-API-Key": "" }
    )
    expect(res.status).toBe(401)
  })

  it("accepts requests with a valid API key", async () => {
    const res = await post({ text: "hello", namespace: "test" })
    expect(res.status).toBe(200)
  })

  it("enforces auth on all routes, not just POST /", async () => {
    const res = await SELF.fetch("https://example.com/any-path", {
      method: "GET",
    })
    expect(res.status).toBe(401)
  })
})

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const res = await post({ namespace: "test" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const res = await post({ text: "hello" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is an empty object", async () => {
    const res = await post({})
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it.each([
    ["number", { text: 123, namespace: "test" }],
    ["boolean", { text: true, namespace: "test" }],
    ["null", { text: null, namespace: "test" }],
    ["array", { text: ["hello"], namespace: "test" }],
    ["object", { text: { nested: "value" }, namespace: "test" }],
  ])("returns 400 when text is a %s", async (_label, body) => {
    const res = await post(body)
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it.each([
    ["number", { text: "hello", namespace: 42 }],
    ["boolean", { text: "hello", namespace: false }],
    ["null", { text: "hello", namespace: null }],
    ["array", { text: "hello", namespace: ["ns"] }],
  ])("returns 400 when namespace is a %s", async (_label, body) => {
    const res = await post(body)
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("accepts extra fields in body without error", async () => {
    const res = await post({
      text: "hello",
      namespace: "test",
      extra: "field",
      another: 42,
    })
    expect(res.status).toBe(200)
  })
})

describe("Similarity Search", () => {
  it("returns a JSON response with similarity_score", async () => {
    const res = await post({ text: "sample message", namespace: "default" })
    expect(res.status).toBe(200)

    const json = await res.json<{ similarity_score: number }>()
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns similarity_score between 0 and 1", async () => {
    const res = await post({ text: "sample message", namespace: "default" })
    const json = await res.json<{ similarity_score: number }>()
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns only similarity_score in the response body", async () => {
    const res = await post({ text: "check response shape", namespace: "ns" })
    const json = await res.json<Record<string, unknown>>()
    expect(Object.keys(json)).toEqual(["similarity_score"])
  })

  it("sets application/json content-type on success", async () => {
    const res = await post({ text: "content type check", namespace: "ns" })
    expect(res.headers.get("content-type")).toContain("application/json")
  })

  it("processes empty string text without error", async () => {
    const res = await post({ text: "", namespace: "test" })
    expect(res.status).toBe(200)
    const json = await res.json<{ similarity_score: number }>()
    expect(typeof json.similarity_score).toBe("number")
  })

  it("processes empty string namespace without error", async () => {
    const res = await post({ text: "hello", namespace: "" })
    expect(res.status).toBe(200)
    const json = await res.json<{ similarity_score: number }>()
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 0 when no matches are found", async () => {
    const res = await post({ text: "no match", namespace: "empty-ns" })
    expect(res.status).toBe(200)
    const json = await res.json<{ similarity_score: number }>()
    expect(json.similarity_score).toBe(0)
  })

  it("handles unicode and special characters in text", async () => {
    const res = await post({
      text: "Zer0 d@y 漏洞 exploit — «вредоносный» 🔒",
      namespace: "test",
    })
    expect(res.status).toBe(200)
    const json = await res.json<{ similarity_score: number }>()
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles whitespace-only text input", async () => {
    const res = await post({ text: "   \t\n  ", namespace: "test" })
    expect(res.status).toBe(200)
  })

  it("handles a large text payload", async () => {
    const largeText = "a]".repeat(50_000)
    const res = await post({ text: largeText, namespace: "test" })
    expect(res.status).toBe(200)
    const json = await res.json<{ similarity_score: number }>()
    expect(typeof json.similarity_score).toBe("number")
  })
})

describe("HTTP Methods", () => {
  it.each(["GET", "PUT", "DELETE", "PATCH", "OPTIONS"])(
    "returns 404 for %s requests",
    async (method) => {
      const res = await req(method)
      expect(res.status).toBe(404)
    }
  )
})

describe("Routing", () => {
  it("returns 404 for POST to an unknown path", async () => {
    const res = await post({ text: "hello", namespace: "test" }, {}, "/unknown")
    expect(res.status).toBe(404)
  })

  it("returns 404 for POST to a nested path", async () => {
    const res = await post(
      { text: "hello", namespace: "test" },
      {},
      "/api/search"
    )
    expect(res.status).toBe(404)
  })
})

describe("Concurrency", () => {
  it("handles multiple concurrent requests correctly", async () => {
    const requests = Array.from({ length: 10 }, (_, i) =>
      post({ text: `message ${i}`, namespace: "test" })
    )
    const responses = await Promise.all(requests)

    for (const res of responses) {
      expect(res.status).toBe(200)
      const json = await res.json<{ similarity_score: number }>()
      expect(json).toHaveProperty("similarity_score")
    }
  })

  it("isolates auth failures from concurrent valid requests", async () => {
    const validReq = post({ text: "valid", namespace: "test" })
    const invalidReq = SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "no auth", namespace: "test" }),
    })

    const [validRes, invalidRes] = await Promise.all([validReq, invalidReq])
    expect(validRes.status).toBe(200)
    expect(invalidRes.status).toBe(401)
  })
})
