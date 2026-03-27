import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const VALID_API_KEY = "test-api-key"
const BASE_URL = "https://example.com/"

function postRequest(body: unknown, apiKey?: string): Request {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }
  if (apiKey) {
    headers["X-API-Key"] = apiKey
  }
  return new Request(BASE_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  })
}

describe("Authentication", () => {
  it("returns 401 when API key is missing", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello", namespace: "test" })
    )
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is invalid", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello", namespace: "test" }, "wrong-key")
    )
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("succeeds with valid API key", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello world", namespace: "test" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
  })
})

describe("Request Validation", () => {
  it("returns 400 when body is missing text field", async () => {
    const response = await SELF.fetch(
      postRequest({ namespace: "test" }, VALID_API_KEY)
    )
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when body is missing namespace field", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello" }, VALID_API_KEY)
    )
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is not a string", async () => {
    const response = await SELF.fetch(
      postRequest({ text: 123, namespace: "test" }, VALID_API_KEY)
    )
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is not a string", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello", namespace: ["test"] }, VALID_API_KEY)
    )
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when both fields are missing", async () => {
    const response = await SELF.fetch(
      postRequest({}, VALID_API_KEY)
    )
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Similarity Search Response", () => {
  it("returns JSON with similarity_score field", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "sample text", namespace: "test-ns" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
    const body = await response.json()
    expect(body).toHaveProperty("similarity_score")
  })

  it("returns numeric similarity score", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "sample text", namespace: "test-ns" }, VALID_API_KEY)
    )
    const body = await response.json()
    expect(typeof body.similarity_score).toBe("number")
  })

  it("returns similarity score in valid range [0, 1]", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "sample text", namespace: "test-ns" }, VALID_API_KEY)
    )
    const body = await response.json()
    expect(body.similarity_score).toBeGreaterThanOrEqual(0)
    expect(body.similarity_score).toBeLessThanOrEqual(1)
  })

  it("returns Content-Type application/json", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "test", namespace: "ns" }, VALID_API_KEY)
    )
    expect(response.headers.get("Content-Type")).toContain("application/json")
  })
})

describe("Edge Cases", () => {
  it("handles empty string text", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "", namespace: "test" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
    const body = await response.json()
    expect(body).toHaveProperty("similarity_score")
  })

  it("handles empty string namespace", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello", namespace: "" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
  })

  it("handles long text input", async () => {
    const longText = "word ".repeat(500).trim()
    const response = await SELF.fetch(
      postRequest({ text: longText, namespace: "test" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
    const body = await response.json()
    expect(body).toHaveProperty("similarity_score")
  })

  it("handles special characters in text", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello 世界 🌍 \n\t special", namespace: "test" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
  })

  it("handles special characters in namespace", async () => {
    const response = await SELF.fetch(
      postRequest({ text: "hello", namespace: "ns-with-dashes_and_underscores.123" }, VALID_API_KEY)
    )
    expect(response.status).toBe(200)
  })
})

describe("HTTP Method Handling", () => {
  it("rejects GET requests", async () => {
    const response = await SELF.fetch(
      new Request(BASE_URL, {
        method: "GET",
        headers: { "X-API-Key": VALID_API_KEY },
      })
    )
    // Hono should not match GET on POST route
    expect(response.status).not.toBe(200)
  })
})
