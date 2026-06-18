import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const endpoint = "https://example.com/"
const validHeaders = {
  "Content-Type": "application/json",
  "X-API-Key": "test-api-key"
}

function postSimilarity(body: unknown, headers = validHeaders) {
  return SELF.fetch(endpoint, {
    method: "POST",
    headers,
    body: typeof body === "string" ? body : JSON.stringify(body)
  })
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing or invalid", async () => {
    const response = await SELF.fetch(endpoint, {
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

describe("Similarity search integration", () => {
  it("returns the top Vectorize score for a valid authenticated request", async () => {
    const response = await postSimilarity({
      text: "Suspicious wallet cluster activity",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0.8765
    })
  })

  it("returns zero when Vectorize has no matches", async () => {
    const response = await postSimilarity({
      text: "No matching record should exist",
      namespace: "empty-namespace"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0
    })
  })
})

describe("Request validation", () => {
  it("returns 400 for malformed JSON", async () => {
    const response = await postSimilarity("{not-json")

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when the JSON body is not an object", async () => {
    const response = await postSimilarity(["text", "namespace"])

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when required fields are not strings", async () => {
    const response = await postSimilarity({
      text: 42,
      namespace: null
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 502 when Workers AI does not return an embedding vector", async () => {
    const response = await postSimilarity({
      text: "simulate missing embedding",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Embedding not found")
  })
})
