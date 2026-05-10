import { SELF } from "cloudflare:test"
import { describe, it, expect } from "vitest"

import "../src/index"

const apiKey = "test-api-key"

function postSimilaritySearch(body: string) {
  return SELF.fetch("https://example.com/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey
    },
    body
  })
}

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

describe("Request parsing", () => {
  it("returns 400 when the request body is malformed JSON", async () => {
    const response = await postSimilaritySearch("{")

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when the JSON body is null", async () => {
    const response = await postSimilaritySearch("null")

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })

  it("returns 400 when the JSON body is an array", async () => {
    const response = await postSimilaritySearch(JSON.stringify([
      {
        text: "Sample text",
        namespace: "test-namespace"
      }
    ]))

    expect(response.status).toBe(400)
    expect(await response.text()).toBe("Invalid JSON format")
  })
})
