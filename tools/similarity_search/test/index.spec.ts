import { SELF, env } from "cloudflare:test"
import { describe, it, expect } from "vitest"
import sampleTextVectorized from "./SampleData/sampleTextVectorized"

import "../src/index"

interface SimilarityCheckResponse {
  similarity_score: number
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "invalid-api-key",
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace",
      }),
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Validation", () => {
  it("returns 400 Invalid JSON format when text is missing", async () => {
    const response = await SELF.fetch("https://example.com", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        namespace: "test-namespace",
      }),
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 Invalid JSON format when namespace is missing", async () => {
    const response = await SELF.fetch("https://example.com", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: "Sample text",
      }),
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Functionality", () => {
  it("runs AI model and gets vectorized string back", async () => {
    const response = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: ["Sample text"],
    })
    expect(response.data[0]).toBe(sampleTextVectorized)
  })

  it("queries vector database and gets proper response", async () => {
    const response = await env.VECTORIZE_INDEX.query(sampleTextVectorized, {
      namespace: "test-namespace",
      topK: 1,
    })
    expect(response).toHaveProperty("matches")
    expect(response.matches.length).toBeGreaterThan(0)
  })

  it("returns similarity score for valid requests", async () => {
    const response = await SELF.fetch("https://example.com", {
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
