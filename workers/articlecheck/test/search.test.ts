import { describe, it, expect } from "vitest"
import { formatSearchResults } from "../src/search"

describe("formatSearchResults", () => {
  it("formats results into XML structure", () => {
    const results = [
      {
        title: "Test Page",
        url: "https://example.com",
        description: "A test page"
      }
    ]

    const formatted = formatSearchResults(results)
    expect(formatted).toContain("<search_results>")
    expect(formatted).toContain("</search_results>")
    expect(formatted).toContain('<item index="1">')
    expect(formatted).toContain("Test Page")
    expect(formatted).toContain("https://example.com")
  })

  it("handles empty results", () => {
    const formatted = formatSearchResults([])
    expect(formatted).toContain("No results found")
  })

  it("numbers multiple results correctly", () => {
    const results = [
      { title: "First", url: "https://a.com", description: "A" },
      { title: "Second", url: "https://b.com", description: "B" },
      { title: "Third", url: "https://c.com", description: "C" }
    ]

    const formatted = formatSearchResults(results)
    expect(formatted).toContain('<item index="1">')
    expect(formatted).toContain('<item index="2">')
    expect(formatted).toContain('<item index="3">')
  })
})
