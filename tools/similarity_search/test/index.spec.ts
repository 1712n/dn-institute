import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const API_KEY = "test-api-key"

/**
 * Helper to make authenticated POST requests.
 */
async function postRequest(
  path: string,
  body: unknown,
  options?: { headers?: Record<string, string>; rawBody?: string }
) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    ...options?.headers
  }

  return SELF.fetch(`https://example.com${path}`, {
    method: "POST",
    headers,
    body: options?.rawBody ?? JSON.stringify(body)
  })
}

// ─── Authentication ──────────────────────────────────────────────

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing or invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// ─── Single Search ───────────────────────────────────────────────

describe("Single Search", () => {
  it("returns similarity_score for valid input", async () => {
    const response = await postRequest("/", {
      text: "Bitcoin price manipulation",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as { similarity_score: number }
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
    expect(json.similarity_score).toBeGreaterThanOrEqual(0)
    expect(json.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns 400 when text is missing", async () => {
    const response = await postRequest("/", { namespace: "ns" })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is missing", async () => {
    const response = await postRequest("/", { text: "hello" })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

// ─── Batch Processing ────────────────────────────────────────────

describe("Batch Processing", () => {
  it("processes a valid batch of items", async () => {
    const response = await postRequest("/batch", {
      items: [
        { text: "Bitcoin", namespace: "crypto" },
        { text: "Ethereum", namespace: "crypto" },
        { text: "Market analysis", namespace: "reports" }
      ]
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as {
      results: Array<{
        text: string
        namespace: string
        similarity_score: number
      }>
    }

    expect(json).toHaveProperty("results")
    expect(json.results).toHaveLength(3)

    // Verify each result has the expected fields
    for (const result of json.results) {
      expect(result).toHaveProperty("text")
      expect(result).toHaveProperty("namespace")
      expect(result).toHaveProperty("similarity_score")
      expect(typeof result.similarity_score).toBe("number")
      expect(result.similarity_score).toBeGreaterThanOrEqual(0)
      expect(result.similarity_score).toBeLessThanOrEqual(1)
    }

    // Verify text and namespace are preserved in order
    expect(json.results[0].text).toBe("Bitcoin")
    expect(json.results[0].namespace).toBe("crypto")
    expect(json.results[1].text).toBe("Ethereum")
    expect(json.results[2].namespace).toBe("reports")
  })

  it("processes a single-item batch", async () => {
    const response = await postRequest("/batch", {
      items: [{ text: "single item", namespace: "ns" }]
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as {
      results: Array<{ similarity_score: number }>
    }
    expect(json.results).toHaveLength(1)
    expect(json.results[0].similarity_score).toBe(0.5678)
  })

  it("returns 400 when items is not an array", async () => {
    const response = await postRequest("/batch", {
      items: "not an array"
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when items is an empty array", async () => {
    const response = await postRequest("/batch", {
      items: []
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when items field is missing", async () => {
    const response = await postRequest("/batch", {
      texts: ["hello"]
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when batch exceeds 100 items", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `text ${i}`,
      namespace: "ns"
    }))

    const response = await postRequest("/batch", { items })

    expect(response.status).toBe(400)
    const body = await response.text()
    expect(body).toContain("Batch size limit exceeded")
  })

  it("accepts exactly 100 items (at the limit)", async () => {
    const items = Array.from({ length: 100 }, (_, i) => ({
      text: `text ${i}`,
      namespace: "ns"
    }))

    const response = await postRequest("/batch", { items })

    expect(response.status).toBe(200)

    const json = (await response.json()) as {
      results: Array<{ similarity_score: number }>
    }
    expect(json.results).toHaveLength(100)
  })

  it("returns 400 when an item has non-string text", async () => {
    const response = await postRequest("/batch", {
      items: [
        { text: "valid", namespace: "ns" },
        { text: 123, namespace: "ns" }
      ]
    })

    expect(response.status).toBe(400)
    const body = await response.text()
    expect(body).toContain("index 1")
  })

  it("returns 400 when an item has non-string namespace", async () => {
    const response = await postRequest("/batch", {
      items: [{ text: "valid", namespace: null }]
    })

    expect(response.status).toBe(400)
    const body = await response.text()
    expect(body).toContain("index 0")
  })

  it("preserves the order of results matching input items", async () => {
    const items = [
      { text: "first", namespace: "a" },
      { text: "second", namespace: "b" },
      { text: "third", namespace: "c" }
    ]

    const response = await postRequest("/batch", { items })

    expect(response.status).toBe(200)

    const json = (await response.json()) as {
      results: Array<{ text: string; namespace: string }>
    }

    expect(json.results[0].text).toBe("first")
    expect(json.results[0].namespace).toBe("a")
    expect(json.results[1].text).toBe("second")
    expect(json.results[1].namespace).toBe("b")
    expect(json.results[2].text).toBe("third")
    expect(json.results[2].namespace).toBe("c")
  })

  it("handles items with unicode and special characters", async () => {
    const response = await postRequest("/batch", {
      items: [
        { text: "特殊字符 🚀", namespace: "unicode" },
        { text: "<script>alert('xss')</script>", namespace: "security" }
      ]
    })

    expect(response.status).toBe(200)

    const json = (await response.json()) as {
      results: Array<{ text: string; similarity_score: number }>
    }
    expect(json.results).toHaveLength(2)
    expect(json.results[0].text).toBe("特殊字符 🚀")
  })

  it("requires authentication for batch endpoint", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        items: [{ text: "test", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(401)
  })
})
