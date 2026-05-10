import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

// 🌰 Helper — fires a POST to the worker with configurable auth and body
const post = (body: unknown, apiKey = "test-api-key") =>
  SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey
    },
    body: JSON.stringify(body)
  })

// 🌰🌰🌰 Authentication — missing and invalid API key cases
describe("🌰 Authentication", () => {
  it("🌰 returns 401 when X-API-Key header is absent", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: "sample", namespace: "test" })
    })
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })

  it("🌰 returns 401 when X-API-Key header is present but wrong", async () => {
    const response = await post({ text: "sample", namespace: "test" }, "wrong-key")
    expect(response.status).toBe(401)
    expect(await response.text()).toBe("Unauthorized")
  })
})

// 🌰🌰🌰 Input validation — malformed and edge-case payloads
describe("🌰 Input validation", () => {
  it("🌰 returns 400 when text field is missing", async () => {
    const response = await post({ namespace: "security-incidents" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("🌰 returns 400 when text is an empty string", async () => {
    const response = await post({ text: "", namespace: "security-incidents" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("🌰 returns 400 when text is whitespace only", async () => {
    const response = await post({ text: "   ", namespace: "security-incidents" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("🌰 returns 400 when namespace field is missing", async () => {
    const response = await post({ text: "suspicious trade cluster" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("🌰 returns 400 when namespace is an empty string", async () => {
    const response = await post({ text: "suspicious trade cluster", namespace: "" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("🌰 returns 400 when namespace is a number instead of string", async () => {
    const response = await post({ text: "suspicious trade cluster", namespace: 42 })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("🌰 returns 400 when text is null", async () => {
    const response = await post({ text: null, namespace: "security-incidents" })
    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})

// 🌰🌰🌰 Similarity search — end-to-end request path through AI and Vectorize
describe("🌰 Similarity search", () => {
  it("🌰 embeds text via bge-base-en-v1.5 and returns the top Vectorize match score", async () => {
    const response = await post({
      text: "Suspicious wallet cluster detected on exchange",
      namespace: "security-incidents"
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(body).toEqual({ similarity_score: 0.8765 })
  })

  it("🌰 returns similarity_score of 0 when Vectorize has no matches for the namespace", async () => {
    const response = await post({
      text: "No matching record should exist here",
      namespace: "empty-namespace"
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(body).toEqual({ similarity_score: 0 })
  })

  it("🌰 handles unicode text through the full worker request path", async () => {
    const response = await post({
      text: "Stablecoin depeg risk flagged in 東京 and São Paulo markets",
      namespace: "unicode-smoke"
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(body).toEqual({ similarity_score: 0.4321 })
  })

  it("🌰 returns a high score for near-duplicate content", async () => {
    const response = await post({
      text: "Flash loan attack drained liquidity pool",
      namespace: "near-duplicate"
    })
    expect(response.status).toBe(200)
    const body = await response.json<{ similarity_score: number }>()
    expect(body.similarity_score).toBeGreaterThan(0.9)
  })

  it("🌰 response Content-Type is application/json", async () => {
    const response = await post({
      text: "Coordinated sell pressure across three venues",
      namespace: "security-incidents"
    })
    expect(response.status).toBe(200)
    expect(response.headers.get("content-type")).toContain("application/json")
  })
})
