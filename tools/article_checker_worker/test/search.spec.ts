/**
 * 🌰 Tests for Brave Search client
 */

import { describe, it, expect } from "vitest"
import { formatSearchResults } from "../src/search"

describe("formatSearchResults", () => {
  it("should format a single result into XML structure", () => {
    const results = [
      {
        url: "https://example.com",
        content: "Web Page Title: Example\nWeb Page URL: https://example.com",
      },
    ]

    const formatted = formatSearchResults(results)
    expect(formatted).toContain("<search_results>")
    expect(formatted).toContain("</search_results>")
    expect(formatted).toContain('<item index="1">')
    expect(formatted).toContain("<page_content>")
    expect(formatted).toContain("Web Page Title: Example")
  })

  it("should format multiple results with correct indices", () => {
    const results = [
      { url: "https://a.com", content: "Result A" },
      { url: "https://b.com", content: "Result B" },
      { url: "https://c.com", content: "Result C" },
    ]

    const formatted = formatSearchResults(results)
    expect(formatted).toContain('<item index="1">')
    expect(formatted).toContain('<item index="2">')
    expect(formatted).toContain('<item index="3">')
    expect(formatted).toContain("Result A")
    expect(formatted).toContain("Result C")
  })

  it("should handle empty results", () => {
    const formatted = formatSearchResults([])
    expect(formatted).toContain("<search_results>")
    expect(formatted).toContain("</search_results>")
    expect(formatted).not.toContain("<item")
  })
})
