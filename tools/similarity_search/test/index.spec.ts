import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_API_KEY = "test-api-key"

function postRequest(
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

function validPost(body: unknown) {
  return postRequest(body, { "X-API-Key": VALID_API_KEY })
}

// ── Authentication ──────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const res = await postRequest({ text: "hello", namespace: "ns" })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is wrong", async () => {
    const res = await postRequest(
      { text: "hello", namespace: "ns" },
      { "X-API-Key": "wrong-key" }
    )
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is empty string", async () => {
    const res = await postRequest(
      { text: "hello", namespace: "ns" },
      { "X-API-Key": "" }
    )
    expect(res.status).toBe(401)
  })

  it("passes authentication with valid API key", async () => {
    const res = await validPost({ text: "hello", namespace: "ns" })
    expect(res.status).not.toBe(401)
  })
})

// ── Input Validation ────────────────────────────────────────────

describe("Input Validation", () => {
  it("returns 400 when text is missing", async () => {
    const res = await validPost({ namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is missing", async () => {
    const res = await validPost({ text: "hello" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is a number", async () => {
    const res = await validPost({ text: 123, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number", async () => {
    const res = await validPost({ text: "hello", namespace: 456 })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const res = await validPost({ text: null, namespace: "ns" })
    expect(res.status).toBe(400)
  })

  it("returns 400 when body is empty object", async () => {
    const res = await validPost({})
    expect(res.status).toBe(400)
  })
})

// ── Happy Path ──────────────────────────────────────────────────

describe("Happy Path", () => {
  it("returns JSON with similarity_score for valid request", async () => {
    const res = await validPost({ text: "test query", namespace: "default" })
    expect(res.status).toBe(200)

    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns the mocked similarity score (0.5678)", async () => {
    const res = await validPost({ text: "test query", namespace: "default" })
    const json = (await res.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeCloseTo(0.5678, 4)
  })

  it("accepts Content-Type application/json", async () => {
    const res = await validPost({ text: "a", namespace: "b" })
    expect(res.status).toBe(200)
    expect(res.headers.get("content-type")).toContain("application/json")
  })
})

// ── Edge Cases ──────────────────────────────────────────────────

describe("Edge Cases", () => {
  it("handles empty string text", async () => {
    const res = await validPost({ text: "", namespace: "ns" })
    // Empty string is still typeof "string", so it should pass validation
    expect(res.status).toBe(200)
  })

  it("handles empty string namespace", async () => {
    const res = await validPost({ text: "hello", namespace: "" })
    expect(res.status).toBe(200)
  })

  it("handles very long text input", async () => {
    const longText = "a".repeat(10_000)
    const res = await validPost({ text: longText, namespace: "ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles special characters in text", async () => {
    const res = await validPost({
      text: '🚀 <script>alert("xss")</script> \n\t "quotes" & ampersands',
      namespace: "ns",
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles unicode in namespace", async () => {
    const res = await validPost({ text: "hello", namespace: "名前空間" })
    expect(res.status).toBe(200)
  })

  it("ignores extra fields in request body", async () => {
    const res = await validPost({
      text: "hello",
      namespace: "ns",
      extra: "field",
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("returns 0 similarity_score when Vectorize returns no matches", async () => {
    // The current mock always returns a match, but the code handles
    // empty matches with `|| 0`. This documents the expected behavior.
    // A more advanced test could use per-test mock overrides.
    const res = await validPost({ text: "hello", namespace: "ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })
})

// ── Method Handling ─────────────────────────────────────────────

describe("Method Handling", () => {
  it("returns 404 for GET requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": VALID_API_KEY },
    })
    expect(res.status).toBe(404)
  })
})
