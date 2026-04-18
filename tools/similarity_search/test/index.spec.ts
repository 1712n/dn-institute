import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

describe("Similarity Search API Integration Tests", () => {
  it("returns 400 when API key is missing or invalid", async () => {
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

  it("returns 400 when input json format is invalid or missing required fields", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        description: "Missing text and namespace"
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("successfully returns similarity score and queries vectorize index via AI embeddings", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "Meaningful lookup text",
        namespace: "docs-v1"
      })
    })

    expect(response.status).toBe(200)
    const json = await response.json()
    
    // As per vitest.config.ts mock, the mock vectorize-index returns 0.5678
    expect(json).toEqual({ similarity_score: 0.5678 })
  })
})
