import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

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

describe("Single message processing", () => {
  it("returns single scalar result when single scalar text is given", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    })
    expect(response.status).toBe(200)
    expect(await response.text()).toEqual('{"similarity_score":0.5678}')
  })
})

describe("Batch message processing", () => {
  it ("limits max inputs", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: [
          "This is a story about an orange cloud",
          "This is a story about a llama",
          "This is a story about a hugging emoji",
          "This is a story about overwhelming courage",
        ],
        namespace: "test-namespace"
      })
    })
    expect(response.status).toBe(400)
    expect(await response.text()).toEqual("Too big input, property `text` can have max 3 items")
  })

  it ("returns array results when multiple texts are given", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key",
      },
      body: JSON.stringify({
        text: [
          "This is a story about an orange cloud",
          "This is a story about a llama",
          "This is a story about a hugging emoji"
        ],
        namespace: "test-namespace"
      })
    })
    expect(response.status).toBe(200)
    expect(await response.text()).toEqual('{"similarity_score":[0.5678,0.5678,0.5678]}')
  })
})
