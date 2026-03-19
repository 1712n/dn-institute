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

  it("returns 401 for batch endpoint without API key", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        items: [{ text: "test", namespace: "ns" }]
      })
    })

    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

describe("Single endpoint (backward compatibility)", () => {
  it("returns 400 for invalid JSON format", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-key"
      },
      body: JSON.stringify({
        text: 123,
        namespace: "test"
      })
    })

    expect(response.status).toBe(400)
  })
})

describe("Batch endpoint", () => {
  it("returns 400 when items is not an array", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-key"
      },
      body: JSON.stringify({
        items: "not-an-array"
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("non-empty array")
  })

  it("returns 400 when items is empty", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-key"
      },
      body: JSON.stringify({
        items: []
      })
    })

    expect(response.status).toBe(400)
  })

  it("returns 400 when batch exceeds max size", async () => {
    const items = Array.from({ length: 101 }, (_, i) => ({
      text: `text-${i}`,
      namespace: "test"
    }))

    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-key"
      },
      body: JSON.stringify({ items })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("maximum")
  })

  it("returns 400 when items have invalid format", async () => {
    const response = await SELF.fetch("https://example.com/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "test-key"
      },
      body: JSON.stringify({
        items: [{ text: 123, namespace: "test" }]
      })
    })

    expect(response.status).toBe(400)
    expect(await response.text()).toContain("string fields")
  })
})
