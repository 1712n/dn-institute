import { SELF, env } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

interface SimilarityCheckResponse {
  similarity_score: number
}

describe("Authentication", () => {
  it("returns 401 when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "invalid-api-key",
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      }),
    })

    expect(response.status).toBe(401)
  })
})

describe("Validation", () => {
  it.each([
    ["text is missing", { namespace: "test-namespace" }],
    ["namespace is missing", { text: "Sample text" }]
  ])("returns 400 when %s", async (description, body) => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify(body)
    })

    expect(response.status).toBe(400)
  })
})

describe("Functionality", () => {
  it("runs AI model and gets vectorized string back", async () => {
    const response = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: ["Sample text"],
    })
    expect(response).toHaveProperty("data")
  })

  it("queries vector database and gets proper response", async () => {
    const response = await env.VECTORIZE_INDEX.query([1, 2, 3], {
      namespace: "test-namespace",
      topK: 1,
    })
    expect(response).toHaveProperty("matches")
    expect(response.matches.length).toBeGreaterThan(0)
  })

  it("returns similarity score for valid requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace",
      }),
    })

    expect(response.status).toBe(200)
    const jsonResponse: SimilarityCheckResponse = await response.json()
    expect(jsonResponse).toHaveProperty("similarity_score")
    expect(typeof jsonResponse.similarity_score).toBe("number")
  })
})
