import { SELF, env } from "cloudflare:test"
import { describe, it, expect, vi } from "vitest"

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
        "X-API-Key": "invalid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
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
  it("queries AI model during main route call", async () => {
    const AICall = vi.spyOn(env.AI, "run")

    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(AICall).toHaveBeenCalledWith("@cf/baai/bge-base-en-v1.5", {
      text: ["Sample text"]
    })
    expect(AICall).toHaveReturnedWith({ data: {} })

    expect(response.status).toBe(200)
  })

  it("queries vector database during main route call", async () => {
    const queryCall = vi.spyOn(env.VECTORIZE_INDEX, "query")

    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(queryCall).toHaveBeenCalledWith(undefined, {
      namespace: "test-namespace",
      topK: 1
    })
    expect(queryCall).toHaveReturnedWith({ matches: [{ score: 0.5678 }] })

    expect(response.status).toBe(200)
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
