import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key",
}

function postRequest(body: unknown, headers?: Record<string, string>) {
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: headers ?? VALID_HEADERS,
    body: typeof body === "string" ? body : JSON.stringify(body),
  })
}

// ── Authentication ──────────────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "hello", namespace: "ns" }),
    })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is wrong", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key",
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" }),
    })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is empty string", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "",
      },
      body: JSON.stringify({ text: "hello", namespace: "ns" }),
    })
    expect(res.status).toBe(401)
    expect(await res.text()).toBe("Unauthorized")
  })
})

// ── Input Validation ────────────────────────────────────────────────────

describe("Input validation", () => {
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

  it("returns 400 when text is a number instead of string", async () => {
    const res = await postRequest({ text: 42, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is a number instead of string", async () => {
    const res = await postRequest({ text: "hello", namespace: 123 })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const res = await postRequest({ text: null, namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is empty object", async () => {
    const res = await postRequest({})
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is an array", async () => {
    const res = await postRequest({ text: ["a", "b"], namespace: "ns" })
    expect(res.status).toBe(400)
    expect(await res.text()).toBe("Invalid JSON format")
  })
})

// ── Successful Similarity Search ────────────────────────────────────────

describe("Similarity search (POST /)", () => {
  it("returns a JSON response with similarity_score", async () => {
    const res = await postRequest({ text: "test message", namespace: "test-ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns the score from the vectorize mock (0.5678)", async () => {
    const res = await postRequest({ text: "any text", namespace: "any-ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json.similarity_score).toBe(0.5678)
  })

  it("accepts empty string for text field", async () => {
    const res = await postRequest({ text: "", namespace: "ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("accepts empty string for namespace field", async () => {
    const res = await postRequest({ text: "hello", namespace: "" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
  })

  it("handles long text input", async () => {
    const longText = "a".repeat(10000)
    const res = await postRequest({ text: longText, namespace: "ns" })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles unicode text input", async () => {
    const res = await postRequest({
      text: "Ethereum price analysis",
      namespace: "crypto",
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })

  it("handles special characters in namespace", async () => {
    const res = await postRequest({
      text: "test",
      namespace: "ns-with_special.chars",
    })
    expect(res.status).toBe(200)
    const json = (await res.json()) as { similarity_score: number }
    expect(typeof json.similarity_score).toBe("number")
  })
})

// ── HTTP Method Handling ────────────────────────────────────────────────

describe("HTTP method handling", () => {
  it("returns 404 for GET requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": "test-api-key" },
    })
    expect(res.status).toBe(404)
  })

  it("returns 404 for PUT requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "PUT",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "hello", namespace: "ns" }),
    })
    expect(res.status).toBe(404)
  })

  it("returns 404 for DELETE requests", async () => {
    const res = await SELF.fetch("https://example.com/", {
      method: "DELETE",
      headers: { "X-API-Key": "test-api-key" },
    })
    expect(res.status).toBe(404)
  })
})

// ── Route Handling ──────────────────────────────────────────────────────

describe("Route handling", () => {
  it("returns 404 for unknown paths", async () => {
    const res = await SELF.fetch("https://example.com/unknown", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "hello", namespace: "ns" }),
    })
    expect(res.status).toBe(404)
  })

  it("returns 404 for nested paths", async () => {
    const res = await SELF.fetch("https://example.com/api/search", {
      method: "POST",
      headers: VALID_HEADERS,
      body: JSON.stringify({ text: "hello", namespace: "ns" }),
    })
    expect(res.status).toBe(404)
  })
})

// ── Response Format ─────────────────────────────────────────────────────

describe("Response format", () => {
  it("returns Content-Type application/json for successful requests", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    expect(res.status).toBe(200)
    expect(res.headers.get("Content-Type")).toContain("application/json")
  })

  it("response body contains only similarity_score key", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    const json = (await res.json()) as Record<string, unknown>
    const keys = Object.keys(json)
    expect(keys).toEqual(["similarity_score"])
  })

  it("similarity_score is between 0 and 1", async () => {
    const res = await postRequest({ text: "test", namespace: "ns" })
    const json = (await res.json()) as { similarity_score: number }
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })
})
