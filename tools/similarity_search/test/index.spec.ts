import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

interface ApiResponse {
  similarity_score: number;
}

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is invalid", async () => {
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
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 400 API key not found when API key is missing", async () => {
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

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("API key not found")
  })
})

describe("Validation", () => {
  it("returns 400 Bad Request when text is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: JSON.stringify({
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 Bad Request when namespace is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text"
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Functionality", () => {
  it("returns similarity score for valid requests", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })

    expect(response.status).toBe(200)
    const jsonResponse: ApiResponse = await response.json()
    expect(jsonResponse).toHaveProperty("similarity_score")
    expect(jsonResponse.similarity_score).toBe("number")
  })

})
