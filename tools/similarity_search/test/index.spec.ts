import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const API_KEY = "test-api-key"
const BASE_URL = "https://example.com/"

describe("Authentication", () => {
  it("returns 401 when API key header is missing", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("returns 401 when API key is invalid", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
      },
      body: JSON.stringify({ text: "Sample text", namespace: "test-namespace" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Request validation", () => {
  const headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
  }

  it("returns 400 when text field is missing", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ namespace: "test-namespace" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace field is missing", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: "Sample text" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when text is not a string", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: 123, namespace: "test-namespace" })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when namespace is not a string", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: "Sample text", namespace: 123 })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

describe("Similarity search", () => {
  const headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
  }

  it("returns similarity score for valid request", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: "hello world", namespace: "test-namespace" })
    })
    expect(response.status).toBe(200)
    const json = await response.json()
    expect(json).toHaveProperty("similarity_score")
    expect(typeof json.similarity_score).toBe("number")
    expect(json.similarity_score).toBe(0.95)
  })

  it("returns 0 when no matches are found", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({
        text: "hello world",
        namespace: "empty-namespace"
      })
    })
    expect(response.status).toBe(200)
    const json = await response.json()
    expect(json.similarity_score).toBe(0)
  })

  it("handles empty text string", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: "", namespace: "test-namespace" })
    })
    expect(response.status).toBe(200)
    const json = await response.json()
    expect(json).toHaveProperty("similarity_score")
    expect(json.similarity_score).toBe(0.95)
  })

  it("handles empty namespace string", async () => {
    const response = await SELF.fetch(BASE_URL, {
      method: "POST",
      headers,
      body: JSON.stringify({ text: "hello", namespace: "" })
    })
    expect(response.status).toBe(200)
    const json = await response.json()
    expect(json).toHaveProperty("similarity_score")
    expect(json.similarity_score).toBe(0.95)
  })
})
