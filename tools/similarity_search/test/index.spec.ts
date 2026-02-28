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

describe("Request validation", () => {
  it("returns 400 when body is missing (but API key is valid)", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      }
      // no body
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when body is invalid JSON (but API key is valid)", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-api-key"
      },
      body: "{not-json"
    })

    expect(response.status).toBe(400)
  })
})
