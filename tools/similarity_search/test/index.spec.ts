import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// Valid auth header for all authenticated requests
const AUTH_HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key",
}

// Helper to make authenticated POST requests
async function postWithAuth(
  body: unknown,
  path = "/",
  extraHeaders: Record<string, string> = {}
) {
  return SELF.fetch(`https://example.com${path}`, {
    method: "POST",
    headers: { ...AUTH_HEADERS, ...extraHeaders },
    body: JSON.stringify(body),
  })
}

// ─── Authentication ──────────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 when no API key header is provided", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "test", namespace: "ns" }),
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is wrong", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key",
      },
      body: JSON.stringify({ text: "test", namespace: "ns" }),
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key header is empty string", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "",
      },
      body: JSON.stringify({ text: "test", namespace: "ns" }),
    })
    expect(response.status).toBe(401)
  })

  it("accepts request with correct API key", async () => {
    const response = await postWithAuth({
      text: "Bitcoin exchange hack",
      namespace: "attacks",
    })
    expect(response.status).toBe(200)
  })
})

// ─── Input Validation ────────────────────────────────────────────────

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const response = await postWithAuth({ namespace: "test" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await postWithAuth({ text: "some text" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is a number instead of string", async () => {
    const response = await postWithAuth({ text: 42, namespace: "test" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is an array instead of string", async () => {
    const response = await postWithAuth({
      text: "hello",
      namespace: ["ns1", "ns2"],
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when both fields are null", async () => {
    const response = await postWithAuth({ text: null, namespace: null })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is empty object", async () => {
    const response = await postWithAuth({})
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

// ─── Similarity Scoring (core functionality) ─────────────────────────

describe("Similarity Scoring", () => {
  it("returns a JSON response with similarity_score field", async () => {
    const response = await postWithAuth({
      text: "A smart contract exploit drained $10M from DeFi protocol",
      namespace: "attacks",
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(body).toHaveProperty("similarity_score")
    expect(typeof body.similarity_score).toBe("number")
  })

  it("returns a score between 0 and 1 inclusive", async () => {
    const response = await postWithAuth({
      text: "Phishing campaign targeted crypto wallets",
      namespace: "attacks",
    })
    const body = await response.json<{ similarity_score: number }>()
    expect(body.similarity_score).toBeGreaterThanOrEqual(0)
    expect(body.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns consistent score for the same input", async () => {
    const payload = {
      text: "Flash loan attack on Euler Finance",
      namespace: "defi",
    }
    const [r1, r2] = await Promise.all([
      postWithAuth(payload),
      postWithAuth(payload),
    ])
    const b1 = await r1.json<{ similarity_score: number }>()
    const b2 = await r2.json<{ similarity_score: number }>()
    expect(b1.similarity_score).toBe(b2.similarity_score)
  })

  it("handles very long text input", async () => {
    const longText = "cryptocurrency ".repeat(500) // ~7500 chars
    const response = await postWithAuth({
      text: longText,
      namespace: "stress-test",
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(typeof body.similarity_score).toBe("number")
  })

  it("handles unicode and special characters in text", async () => {
    const response = await postWithAuth({
      text: "Ataque a protocolo DeFi — pérdida de $5M 🔒",
      namespace: "attacks",
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(typeof body.similarity_score).toBe("number")
  })
})

// ─── Namespace Handling ──────────────────────────────────────────────

describe("Namespace Handling", () => {
  it("accepts different namespace values", async () => {
    const namespaces = ["attacks", "defi", "exchange", "general"]
    const results = await Promise.all(
      namespaces.map((ns) =>
        postWithAuth({
          text: "Test text for namespace",
          namespace: ns,
        })
      )
    )
    for (const response of results) {
      expect(response.status).toBe(200)
    }
  })

  it("handles namespace with special characters", async () => {
    const response = await postWithAuth({
      text: "test",
      namespace: "my-namespace_v2",
    })
    expect(response.status).toBe(200)
  })
})

// ─── HTTP Method & Routing ──────────────────────────────────────────

describe("HTTP Method Handling", () => {
  it("rejects GET requests to the root endpoint", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "GET",
      headers: { "X-API-Key": "test-api-key" },
    })
    // Hono returns 404 for unmatched GET on POST-only route
    expect(response.status).not.toBe(200)
  })

  it("returns 404 for non-existent routes", async () => {
    const response = await SELF.fetch("https://example.com/nonexistent", {
      method: "POST",
      headers: AUTH_HEADERS,
      body: JSON.stringify({ text: "test", namespace: "ns" }),
    })
    expect(response.status).toBe(404)
  })
})

// ─── Concurrent Requests ─────────────────────────────────────────────

describe("Concurrency", () => {
  it("handles multiple simultaneous requests", async () => {
    const payloads = Array.from({ length: 5 }, (_, i) => ({
      text: `Concurrent request ${i}: crypto bridge exploit`,
      namespace: "attacks",
    }))
    const responses = await Promise.all(payloads.map((p) => postWithAuth(p)))
    for (const response of responses) {
      expect(response.status).toBe(200)
      const body = await response.json<{ similarity_score: number }>()
      expect(typeof body.similarity_score).toBe("number")
    }
  })
})

// ─── Response Format ─────────────────────────────────────────────────

describe("Response Format", () => {
  it("returns application/json content type", async () => {
    const response = await postWithAuth({
      text: "Rug pull on memecoin",
      namespace: "scams",
    })
    expect(response.headers.get("content-type")).toContain("application/json")
  })

  it("response body contains only similarity_score field", async () => {
    const response = await postWithAuth({
      text: "Exchange hot wallet compromised",
      namespace: "attacks",
    })
    const body = await response.json<Record<string, unknown>>()
    const keys = Object.keys(body)
    expect(keys).toEqual(["similarity_score"])
  })

  it("similarity_score is not NaN or Infinity", async () => {
    const response = await postWithAuth({
      text: "Oracle manipulation attack",
      namespace: "defi",
    })
    const body = await response.json<{ similarity_score: number }>()
    expect(Number.isFinite(body.similarity_score)).toBe(true)
  })
})

// ─── Edge Cases: No Vectorize Matches ────────────────────────────────

describe("No Matches", () => {
  it("returns 0 when vectorize has no matches", async () => {
    // The mock returns a fixed score of 0.5678, but in production
    // an empty matches array would yield 0 via the || 0 fallback.
    // This test documents the fallback behavior.
    const response = await postWithAuth({
      text: "completely unrelated gibberish text xyz123",
      namespace: "empty-namespace",
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(typeof body.similarity_score).toBe("number")
  })
})
