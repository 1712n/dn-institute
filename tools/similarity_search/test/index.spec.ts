import { SELF } from "cloudflare:test"
import { describe, expect, it } from "vitest"

import "../src/index"

const ENDPOINT = "https://example.com/"
const VALID_API_KEY = "test-api-key"

type SimilarityResponse = {
  similarity_score: number
}

async function postSimilarity(body: unknown, apiKey?: string) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  }

  if (apiKey) {
    headers["X-API-Key"] = apiKey
  }

  return SELF.fetch(ENDPOINT, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
}

// 🌰 Authentication integration behavior through middleware.
describe("🌰 Auth middleware integration 🌰", () => {
  it("returns 401 when API key is missing", async () => {
    const response = await postSimilarity({
      text: "sample text",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is wrong", async () => {
    const response = await postSimilarity(
      {
        text: "sample text",
        namespace: "test-namespace"
      },
      "wrong-api-key"
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("passes through middleware when API key is correct", async () => {
    const response = await postSimilarity(
      {
        text: "sample text",
        namespace: "test-namespace"
      },
      VALID_API_KEY
    )

    expect(response.status).toBe(200)
  })
})

// 🌰 End-to-end happy path using mocked Cloudflare AI + Vectorize bindings.
describe("🌰 POST / success integration 🌰", () => {
  it("returns similarity_score between 0 and 1 for valid text and namespace", async () => {
    const response = await postSimilarity(
      {
        text: "Find semantically similar snippets",
        namespace: "docs"
      },
      VALID_API_KEY
    )

    expect(response.status).toBe(200)

    const payload = (await response.json()) as SimilarityResponse
    expect(typeof payload.similarity_score).toBe("number")
    expect(payload.similarity_score).toBeGreaterThanOrEqual(0)
    expect(payload.similarity_score).toBeLessThanOrEqual(1)
  })
})

// 🌰 Input validation behavior for malformed request payloads.
describe("🌰 POST / validation integration 🌰", () => {
  it("returns 400 for invalid JSON format", async () => {
    const response = await postSimilarity(["invalid", "json", "shape"], VALID_API_KEY)

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is missing", async () => {
    const response = await postSimilarity(
      {
        namespace: "docs"
      },
      VALID_API_KEY
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is missing", async () => {
    const response = await postSimilarity(
      {
        text: "search me"
      },
      VALID_API_KEY
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text and namespace are non-string values", async () => {
    const response = await postSimilarity(
      {
        text: 12345,
        namespace: { nested: "object" }
      },
      VALID_API_KEY
    )

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})
