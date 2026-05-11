import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const similaritySearchUrl = "https://example.com/"
const validHeaders = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

function postSimilarity(body: unknown, headers: Record<string, string> = validHeaders) {
  return SELF.fetch(similaritySearchUrl, {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  })
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing or invalid", async () => {
    const response = await postSimilarity({
      text: "Sample text",
      namespace: "known-namespace"
    }, {
      "Content-Type": "application/json"
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Similarity Search integration", () => {
  it("returns the top Vectorize similarity score for a valid request", async () => {
    const response = await postSimilarity({
      text: "Near duplicate claim text",
      namespace: "known-namespace"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0.8765
    })
  })

  it("returns zero when Vectorize has no matches", async () => {
    const response = await postSimilarity({
      text: "Completely new claim text",
      namespace: "empty-namespace"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0
    })
  })

  it("rejects requests that do not include string text and namespace fields", async () => {
    const response = await postSimilarity({
      text: "Missing namespace"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})
