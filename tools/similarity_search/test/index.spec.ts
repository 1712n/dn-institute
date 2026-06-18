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

function post(body: unknown, path = "/") {
  return SELF.fetch(`https://example.com${path}`, {
    method: "POST",
    headers: validHeaders(),
    body: typeof body === "string" ? body : JSON.stringify(body),
  })
}

function batchPost(body: unknown) {
  return post(body, "/batch")
}

function makeItems(count: number, overrides?: Partial<{ text: string; namespace: string }>) {
  return Array.from({ length: count }, (_, i) => ({
    text: overrides?.text ?? `message ${i}`,
    namespace: overrides?.namespace ?? "test",
  }))
}

// ============================================================
// Single endpoint (POST /) — existing functionality
// ============================================================

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
    const res = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { ...validHeaders(), "X-API-Key": "wrong-key" },
      body: JSON.stringify({ text: "hello", namespace: "test" }),
    })
    expect(res.status).toBe(401)
  })

  it("accepts requests with a valid API key", async () => {
    const res = await post({ text: "hello", namespace: "test" })
    expect(res.status).toBe(200)
  })
})

describe("Single endpoint — POST /", () => {
  it("returns similarity_score for valid input", async () => {
    const res = await post({ text: "sample message", namespace: "default" })
    expect(res.status).toBe(200)
    const json = await res.json<{ similarity_score: number }>()
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
  })

  it("returns 400 when text is missing", async () => {
    const res = await post({ namespace: "test" })
    expect(res.status).toBe(400)
  })

  it("returns 400 when namespace is missing", async () => {
    const res = await post({ text: "hello" })
    expect(res.status).toBe(400)
  })

  it("returns 400 for non-string text", async () => {
    const res = await post({ text: 123, namespace: "test" })
    expect(res.status).toBe(400)
  })
})

// ============================================================
// Batch endpoint (POST /batch) — new functionality
// ============================================================

describe("Batch endpoint — Authentication", () => {
  it("rejects batch requests without API key", async () => {
    const res = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: [{ text: "hello", namespace: "test" }] }),
    })
    expect(res.status).toBe(401)
  })

  it("rejects batch requests with invalid API key", async () => {
    const res = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { ...validHeaders(), "X-API-Key": "bad" },
      body: JSON.stringify({ items: [{ text: "hello", namespace: "test" }] }),
    })
    expect(res.status).toBe(401)
  })
})

describe("Batch endpoint — Input validation", () => {
  it("returns 400 for malformed JSON body", async () => {
    const res = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: validHeaders(),
      body: "not valid json{{{",
    })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("Invalid JSON")
  })

  it("returns 400 when items is not an array", async () => {
    const res = await batchPost({ items: "not an array" })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("items must be an array")
  })

  it("returns 400 when items is an object", async () => {
    const res = await batchPost({ items: { text: "hello", namespace: "test" } })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("items must be an array")
  })

  it("returns 400 when items is empty", async () => {
    const res = await batchPost({ items: [] })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("must not be empty")
  })

  it("returns 400 when items exceeds max batch size", async () => {
    const items = makeItems(101)
    const res = await batchPost({ items })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("maximum of 100")
  })

  it("returns 400 when an item has non-string text", async () => {
    const res = await batchPost({
      items: [{ text: 42, namespace: "test" }],
    })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("index 0")
  })

  it("returns 400 when an item has non-string namespace", async () => {
    const res = await batchPost({
      items: [{ text: "hello", namespace: null }],
    })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("index 0")
  })

  it("returns 400 with correct index for invalid item in middle", async () => {
    const res = await batchPost({
      items: [
        { text: "valid", namespace: "test" },
        { text: "also valid", namespace: "test" },
        { text: 999, namespace: "test" },
      ],
    })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("index 2")
  })

  it("returns 400 when text exceeds max length", async () => {
    const longText = "x".repeat(8193)
    const res = await batchPost({
      items: [{ text: longText, namespace: "test" }],
    })
    expect(res.status).toBe(400)
    const json = await res.json<{ error: string }>()
    expect(json.error).toContain("maximum text length")
  })

  it("accepts text at exactly max length", async () => {
    const maxText = "x".repeat(8192)
    const res = await batchPost({
      items: [{ text: maxText, namespace: "test" }],
    })
    expect(res.status).toBe(200)
  })

  it("returns 400 when items field is missing entirely", async () => {
    const res = await batchPost({ messages: [{ text: "hi", namespace: "x" }] })
    expect(res.status).toBe(400)
  })
})

describe("Batch endpoint — Successful processing", () => {
  it("returns results array with correct length", async () => {
    const items = makeItems(3)
    const res = await batchPost({ items })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: unknown[] }>()
    expect(json.results).toHaveLength(3)
  })

  it("returns similarity_score for each item", async () => {
    const items = makeItems(5)
    const res = await batchPost({ items })
    const json = await res.json<{ results: { similarity_score: number }[] }>()
    for (const result of json.results) {
      expect(result).toHaveProperty("similarity_score")
      expect(typeof result.similarity_score).toBe("number")
      expect(result.similarity_score).toBeGreaterThanOrEqual(0)
      expect(result.similarity_score).toBeLessThanOrEqual(1)
    }
  })

  it("echoes text and namespace in each result", async () => {
    const items = [
      { text: "alpha", namespace: "ns-a" },
      { text: "beta", namespace: "ns-b" },
    ]
    const res = await batchPost({ items })
    const json = await res.json<{ results: { text: string; namespace: string }[] }>()
    expect(json.results[0].text).toBe("alpha")
    expect(json.results[0].namespace).toBe("ns-a")
    expect(json.results[1].text).toBe("beta")
    expect(json.results[1].namespace).toBe("ns-b")
  })

  it("preserves input order in results", async () => {
    const texts = ["first", "second", "third", "fourth", "fifth"]
    const items = texts.map((t) => ({ text: t, namespace: "test" }))
    const res = await batchPost({ items })
    const json = await res.json<{ results: { text: string }[] }>()
    json.results.forEach((r, i) => {
      expect(r.text).toBe(texts[i])
    })
  })

  it("handles a single item batch", async () => {
    const res = await batchPost({
      items: [{ text: "solo", namespace: "test" }],
    })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: unknown[] }>()
    expect(json.results).toHaveLength(1)
  })

  it("processes items with different namespaces", async () => {
    const items = [
      { text: "msg", namespace: "ns-1" },
      { text: "msg", namespace: "ns-2" },
      { text: "msg", namespace: "ns-3" },
    ]
    const res = await batchPost({ items })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: { namespace: string }[] }>()
    expect(json.results[0].namespace).toBe("ns-1")
    expect(json.results[1].namespace).toBe("ns-2")
    expect(json.results[2].namespace).toBe("ns-3")
  })

  it("returns application/json content-type", async () => {
    const res = await batchPost({ items: makeItems(1) })
    expect(res.headers.get("content-type")).toContain("application/json")
  })

  it("returns 0 score when no vectorize matches exist", async () => {
    const res = await batchPost({
      items: [{ text: "no match here", namespace: "empty-ns" }],
    })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: { similarity_score: number }[] }>()
    expect(json.results[0].similarity_score).toBe(0)
  })
})

describe("Batch endpoint — Deduplication", () => {
  it("handles duplicate texts efficiently", async () => {
    const items = [
      { text: "duplicate", namespace: "ns-a" },
      { text: "duplicate", namespace: "ns-b" },
      { text: "duplicate", namespace: "ns-c" },
    ]
    const res = await batchPost({ items })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: { text: string; namespace: string }[] }>()
    expect(json.results).toHaveLength(3)
    // All share the same text but different namespaces
    expect(json.results[0].namespace).toBe("ns-a")
    expect(json.results[1].namespace).toBe("ns-b")
    expect(json.results[2].namespace).toBe("ns-c")
  })

  it("deduplicates identical items correctly", async () => {
    const items = [
      { text: "same", namespace: "same-ns" },
      { text: "same", namespace: "same-ns" },
    ]
    const res = await batchPost({ items })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: { similarity_score: number }[] }>()
    expect(json.results).toHaveLength(2)
    expect(json.results[0].similarity_score).toBe(json.results[1].similarity_score)
  })
})

describe("Batch endpoint — Edge cases", () => {
  it("handles unicode text", async () => {
    const res = await batchPost({
      items: [
        { text: "Exploit 漏洞 — «вредоносный»", namespace: "test" },
        { text: "Sicherheitslucke", namespace: "test" },
      ],
    })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: unknown[] }>()
    expect(json.results).toHaveLength(2)
  })

  it("handles empty string text", async () => {
    const res = await batchPost({
      items: [{ text: "", namespace: "test" }],
    })
    expect(res.status).toBe(200)
  })

  it("handles empty string namespace", async () => {
    const res = await batchPost({
      items: [{ text: "hello", namespace: "" }],
    })
    expect(res.status).toBe(200)
  })

  it("handles batch at exactly max size", async () => {
    const items = makeItems(100)
    const res = await batchPost({ items })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: unknown[] }>()
    expect(json.results).toHaveLength(100)
  })

  it("handles mixed valid namespaces including empty-ns", async () => {
    const items = [
      { text: "has match", namespace: "test" },
      { text: "no match", namespace: "empty-ns" },
    ]
    const res = await batchPost({ items })
    expect(res.status).toBe(200)
    const json = await res.json<{ results: { similarity_score: number }[] }>()
    expect(json.results[0].similarity_score).toBeGreaterThan(0)
    expect(json.results[1].similarity_score).toBe(0)
  })

  it("handles whitespace-only text", async () => {
    const res = await batchPost({
      items: [{ text: "   \t\n  ", namespace: "test" }],
    })
    expect(res.status).toBe(200)
  })
})

describe("Batch endpoint — Concurrency", () => {
  it("handles concurrent batch requests", async () => {
    const requests = Array.from({ length: 5 }, (_, i) =>
      batchPost({ items: makeItems(3, { text: `concurrent-${i}` }) })
    )
    const responses = await Promise.all(requests)
    for (const res of responses) {
      expect(res.status).toBe(200)
      const json = await res.json<{ results: unknown[] }>()
      expect(json.results).toHaveLength(3)
    }
  })
})

describe("HTTP methods", () => {
  it.each(["GET", "PUT", "DELETE", "PATCH"])(
    "returns 404 for %s on /batch",
    async (method) => {
      const res = await SELF.fetch("https://example.com/batch", {
        method,
        headers: validHeaders(),
      })
      expect(res.status).toBe(404)
    }
  )
})

describe("Routing", () => {
  it("returns 404 for POST to unknown path", async () => {
    const res = await post({ text: "hello", namespace: "test" }, "/unknown")
    expect(res.status).toBe(404)
  })

  it("keeps single endpoint and batch endpoint independent", async () => {
    const singleRes = await post({ text: "hello", namespace: "test" })
    const batchRes = await batchPost({
      items: [{ text: "hello", namespace: "test" }],
    })
    expect(singleRes.status).toBe(200)
    expect(batchRes.status).toBe(200)

    const singleJson = await singleRes.json<{ similarity_score: number }>()
    const batchJson = await batchRes.json<{ results: { similarity_score: number }[] }>()
    expect(singleJson.similarity_score).toBe(batchJson.results[0].similarity_score)
  })
})
