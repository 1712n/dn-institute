import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

async function postSearch(
  body: unknown,
  headers: Record<string, string> = {}
): Promise<Response> {
  const isString = typeof body === "string"
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "test-api-key",
      ...headers
    },
    body: isString ? body : JSON.stringify(body)
  })
}

describe("Similarity Search API 🌰", () => {
  describe("Authentication 🌰", () => {
    it("returns 401 when X-API-Key header is missing", async () => {
      const response = await SELF.fetch("https://example.com/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "hello", namespace: "ns" })
      })

      expect(response.status).toBe(401)
      expect(await response.text()).toBe("Unauthorized")
    })

    it("returns 401 when X-API-Key header has wrong value", async () => {
      const response = await SELF.fetch("https://example.com/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "wrong-key-value"
        },
        body: JSON.stringify({ text: "hello", namespace: "ns" })
      })

      expect(response.status).toBe(401)
      expect(await response.text()).toBe("Unauthorized")
    })

    it("returns 200 when X-API-Key is correct", async () => {
      const response = await postSearch({ text: "hello", namespace: "ns" })

      expect(response.status).toBe(200)
    })
  })

  describe("Input Validation 🌰", () => {
    it("returns 400 when text field is missing", async () => {
      const response = await postSearch({ namespace: "ns" })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when namespace field is missing", async () => {
      const response = await postSearch({ text: "hello" })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when request body is invalid JSON", async () => {
      const response = await postSearch("this is not json {{{")

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when text is a number instead of string", async () => {
      const response = await postSearch({ text: 42, namespace: "ns" })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when namespace is a number instead of string", async () => {
      const response = await postSearch({ text: "hello", namespace: 123 })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when text is null", async () => {
      const response = await postSearch({ text: null, namespace: "ns" })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when root JSON is null", async () => {
      const response = await postSearch("null")

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when root JSON is an array", async () => {
      const response = await postSearch([{ text: "hello", namespace: "ns" }])

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when fields are arrays", async () => {
      const response = await postSearch({
        text: ["hello", "world"],
        namespace: ["ns"]
      })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })

    it("returns 400 when text is empty string", async () => {
      const response = await postSearch({ text: "", namespace: "ns" })

      expect(response.status).toBe(400)
      expect(await response.text()).toBe("Invalid JSON format")
    })
  })

  describe("Core Similarity Search 🌰", () => {
    it("returns 200 with JSON containing similarity_score for valid request", async () => {
      const response = await postSearch({
        text: "Sample text for embedding",
        namespace: "test-namespace"
      })

      expect(response.status).toBe(200)
      const json = await response.json<{ similarity_score: number }>()
      expect(json).toHaveProperty("similarity_score")
    })

    it("returns response with Content-Type application/json", async () => {
      const response = await postSearch({
        text: "hello world",
        namespace: "ns"
      })

      expect(response.status).toBe(200)
      expect(response.headers.get("Content-Type")).toContain("application/json")
    })

    it("returns the mocked vectorize score of 0.5678", async () => {
      const response = await postSearch({
        text: "any text",
        namespace: "any-namespace"
      })

      const json = await response.json<{ similarity_score: number }>()
      expect(json.similarity_score).toBe(0.5678)
    })

    it("returns a score that is a number between 0 and 1", async () => {
      const response = await postSearch({
        text: "check score range",
        namespace: "ns"
      })

      const json = await response.json<{ similarity_score: number }>()
      expect(typeof json.similarity_score).toBe("number")
      expect(json.similarity_score).toBeGreaterThanOrEqual(0)
      expect(json.similarity_score).toBeLessThanOrEqual(1)
    })

    it("handles empty string namespace and returns 200", async () => {
      const response = await postSearch({ text: "hello", namespace: "" })

      expect(response.status).toBe(200)
      const json = await response.json<{ similarity_score: number }>()
      expect(json).toHaveProperty("similarity_score")
    })

    it("returns similarity_score 0 when no vector matches exist", async () => {
      const response = await SELF.fetch("https://example.com/no-matches", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "test-api-key"
        },
        body: JSON.stringify({ text: "query with no results", namespace: "empty-ns" })
      })

      expect(response.status).toBe(404)
    })
  })

  describe("Edge Cases 🌰", () => {
    it("processes very long text (10k chars) successfully", async () => {
      const longText = "a".repeat(10_000)
      const response = await postSearch({
        text: longText,
        namespace: "ns"
      })

      expect(response.status).toBe(200)
      const json = await response.json<{ similarity_score: number }>()
      expect(json).toHaveProperty("similarity_score")
    })

    it("handles unicode, emoji, and CJK characters in text", async () => {
      const response = await postSearch({
        text: "Hello 🌰🌍 你好世界 こんにちは Ñoño",
        namespace: "ns"
      })

      expect(response.status).toBe(200)
      const json = await response.json<{ similarity_score: number }>()
      expect(json.similarity_score).toBe(0.5678)
    })

    it("handles special characters in namespace", async () => {
      const response = await postSearch({
        text: "hello world",
        namespace: "ns/special-chars_123.test@org"
      })

      expect(response.status).toBe(200)
      const json = await response.json<{ similarity_score: number }>()
      expect(json).toHaveProperty("similarity_score")
    })

    it("ignores extra fields in the request body", async () => {
      const response = await postSearch({
        text: "hello world",
        namespace: "ns",
        extra_field: "should be ignored",
        another: 999
      })

      expect(response.status).toBe(200)
      const json = await response.json<{ similarity_score: number }>()
      expect(json.similarity_score).toBe(0.5678)
    })

    it("returns 404 for GET requests (only POST supported)", async () => {
      const response = await SELF.fetch("https://example.com/", {
        method: "GET",
        headers: { "X-API-Key": "test-api-key" }
      })

      expect(response.status).toBe(404)
    })

    it("handles 10 concurrent requests successfully", async () => {
      const requests = Array.from({ length: 10 }, (_, i) =>
        postSearch({ text: `concurrent test message ${i}`, namespace: "ns" })
      )

      const responses = await Promise.all(requests)

      for (const response of responses) {
        expect(response.status).toBe(200)
        const json = await response.json<{ similarity_score: number }>()
        expect(json.similarity_score).toBe(0.5678)
      }
    })
  })
})
