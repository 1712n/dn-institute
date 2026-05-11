import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const postSearch = (body: Record<string, unknown>) =>
  SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "test-api-key"
    },
    body: JSON.stringify(body)
  })

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

describe("Similarity search integration", () => {
  it("returns the Vectorize similarity score for a valid search request", async () => {
    const response = await postSearch({
      text: "Sample text",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({ similarity_score: 0.5678 })
  })

  it("returns 0 when Vectorize returns no matches", async () => {
    const response = await postSearch({
      text: "Sample text",
      namespace: "no-match"
    })

    expect(response.status).toBe(200)
    expect(await response.json()).toEqual({ similarity_score: 0 })
  })
})

describe("Upstream dependency failures", () => {
  it("returns 502 when Workers AI cannot generate an embedding", async () => {
    const response = await postSearch({
      text: "trigger-ai-error",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Embedding generation failed")
  })

  it("returns 502 when Workers AI returns no embedding vector", async () => {
    const response = await postSearch({
      text: "empty-embedding",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Embedding generation failed")
  })

  it("returns 502 when Workers AI returns a malformed embedding vector", async () => {
    const response = await postSearch({
      text: "invalid-embedding",
      namespace: "test-namespace"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Embedding generation failed")
  })

  it("returns 502 when Vectorize cannot complete the similarity lookup", async () => {
    const response = await postSearch({
      text: "Sample text",
      namespace: "trigger-vectorize-error"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Similarity search failed")
  })
})
