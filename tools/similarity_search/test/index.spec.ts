import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const apiKey = "test-api-key"

const postSimilaritySearch = (body: unknown, apiKeyHeader = apiKey) => {
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKeyHeader
    },
    body: JSON.stringify(body)
  })
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing", async () => {
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

  it("returns 401 Unauthorized when API key is invalid", async () => {
    const response = await postSimilaritySearch(
      {
        text: "Sample text",
        namespace: "test-namespace"
      },
      "wrong-api-key"
    )

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Request validation", () => {
  it("returns 400 when text is missing", async () => {
    const response = await postSimilaritySearch({
      namespace: "security-incidents"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is empty", async () => {
    const response = await postSimilaritySearch({
      text: "",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is only whitespace", async () => {
    const response = await postSimilaritySearch({
      text: "  \t  ",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is not a string", async () => {
    const response = await postSimilaritySearch({
      text: "duplicate message",
      namespace: 42
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is null", async () => {
    const response = await postSimilaritySearch({
      text: null,
      namespace: "security-incidents"
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is null", async () => {
    const response = await postSimilaritySearch({
      text: "duplicate message",
      namespace: null
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Similarity search", () => {
  it("embeds the request text and returns the top Vectorize match score", async () => {
    const response = await postSimilaritySearch({
      text: "Suspicious wallet cluster activity",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0.8765
    })
  })

  it("returns zero when Vectorize has no matches for the namespace", async () => {
    const response = await postSimilaritySearch({
      text: "No matching record should exist",
      namespace: "empty-namespace"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0
    })
  })

  it("handles unicode input through the full worker request path", async () => {
    const response = await postSimilaritySearch({
      text: "Similar alert: stablecoin depeg risk increased in 東京 markets",
      namespace: "unicode-smoke-test"
    })

    expect(response.status).toBe(200)
    await expect(response.json()).resolves.toEqual({
      similarity_score: 0.4321
    })
  })

  it("returns 502 when Workers AI embedding fails", async () => {
    const response = await postSimilaritySearch({
      text: "trigger-workers-ai-failure",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Workers AI request failed")
  })

  it("returns 502 when Workers AI returns an invalid response shape", async () => {
    const response = await postSimilaritySearch({
      text: "trigger-workers-ai-empty-response",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Workers AI request failed")
  })

  it("returns 502 when Workers AI returns a non-numeric vector", async () => {
    const response = await postSimilaritySearch({
      text: "trigger-workers-ai-invalid-vector",
      namespace: "security-incidents"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Workers AI request failed")
  })

  it("returns 502 when Vectorize query fails", async () => {
    const response = await postSimilaritySearch({
      text: "Vectorize boundary failure should be handled",
      namespace: "vectorize-failure"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Vectorize query failed")
  })

  it("returns 502 when Vectorize returns an invalid response shape", async () => {
    const response = await postSimilaritySearch({
      text: "Malformed Vectorize response should be handled",
      namespace: "vectorize-invalid-response"
    })

    expect(response.status).toBe(502)
    expect(await response.text()).toBe("Vectorize query failed")
  })
})
