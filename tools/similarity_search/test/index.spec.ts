import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const validHeaders = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

function postSimilaritySearch(text: string, namespace = "test-namespace") {
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: validHeaders,
    body: JSON.stringify({ text, namespace })
  })
}

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

describe("Similarity search dependencies", () => {
  it("returns the top Vectorize score for a valid request", async () => {
    const response = await postSimilaritySearch("Sample text")

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0.5678
    })
  })

  it("returns zero when Vectorize has no matches", async () => {
    const response = await postSimilaritySearch("Sample text", "no-matches")

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0
    })
  })

  it("returns 502 when Workers AI embedding generation fails", async () => {
    const response = await postSimilaritySearch("trigger-ai-error")

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Similarity search dependency failed")
  })

  it("returns 502 when Workers AI returns no embedding vector", async () => {
    const response = await postSimilaritySearch("trigger-invalid-embedding")

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Similarity search dependency failed")
  })

  it("returns 502 when the Vectorize query fails", async () => {
    const response = await postSimilaritySearch("Sample text", "vectorize-error")

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Similarity search dependency failed")
  })
})
