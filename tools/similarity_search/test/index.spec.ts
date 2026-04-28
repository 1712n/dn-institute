import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

describe("Authentication", () => {
  it("returns 401 Unauthorized when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "Sample text", namespace: "test" })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
      },
      body: JSON.stringify({ text: "Sample text", namespace: "test" })
    })

    expect(response.status).toBe(401)
  })

  it("returns 400 when API key is missing from env", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "test", namespace: "ns" })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("API key not found")
  })
})

describe("Input Validation", () => {
  it("returns 400 when text field is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ namespace: "test-ns" })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ text: "Sample text" })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when text is not a string", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ text: 123, namespace: "ns" })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when namespace is not a string", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ text: "Sample text", namespace: 123 })
    })

    expect(response.status).toBe(400)
  })
})

describe("Similarity Search", () => {
  it("returns similarity_score on valid request", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "machine learning",
        namespace: "ai-topics"
      })
    })

    expect(response.status).toBe(200)
    
    const data = await response.json()
    expect(data).toHaveProperty("similarity_score")
    expect(typeof data.similarity_score).toBe("number")
  })

  it("returns valid similarity score from vector search", async () => {
    const text = "deep neural networks"
    const namespace = "ml"
    
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ text, namespace })
    })

    const data = await response.json()
    // Mock returns 0.5678 from vitest config
    expect(data.similarity_score).toBe(0.5678)
  })

  it("handles empty text gracefully", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ text: "", namespace: "ns" })
    })

    // Empty string is still a valid string
    expect(response.status).toBe(200)
  })

  it("handles long text input", async () => {
    const longText = " ".join(["word"] * 1000)
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({ text: longText, namespace: "ns" })
    })

    expect(response.status).toBe(200)
  })

  it("handles special characters in text", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: JSON.stringify({
        text: "NFT #1234 @user $100!",
        namespace: "social"
      })
    })

    expect(response.status).toBe(200)
  })
})