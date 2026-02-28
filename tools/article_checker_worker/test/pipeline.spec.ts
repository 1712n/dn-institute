/**
 * 🌰 Tests for the fact-checking pipeline
 */

import { describe, it, expect } from "vitest"
import { extractBetweenTags } from "../src/pipeline"

describe("extractBetweenTags", () => {
  it("should extract content between tags", () => {
    const text = "<statement>Test statement</statement>"
    expect(extractBetweenTags("statement", text)).toBe("Test statement")
  })

  it("should return the last match when multiple exist", () => {
    const text =
      "<statement>First</statement> <statement>Second</statement>"
    expect(extractBetweenTags("statement", text)).toBe("Second")
  })

  it("should return null when no match found", () => {
    expect(extractBetweenTags("missing", "no tags here")).toBeNull()
  })

  it("should handle multiline content", () => {
    const text = "<answer>\nLine 1\nLine 2\nLine 3\n</answer>"
    const result = extractBetweenTags("answer", text)
    expect(result).toContain("Line 1")
    expect(result).toContain("Line 3")
  })

  it("should trim whitespace", () => {
    const text = "<verdict>  True  </verdict>"
    expect(extractBetweenTags("verdict", text)).toBe("True")
  })

  it("should handle nested XML-like content", () => {
    const text =
      "<search_query>crypto hack 2024 losses</search_query>"
    expect(extractBetweenTags("search_query", text)).toBe(
      "crypto hack 2024 losses"
    )
  })

  it("should extract number_of_statements", () => {
    const text =
      "<statement>S1</statement>\n<statement>S2</statement>\n<number_of_statements>2</number_of_statements>"
    expect(extractBetweenTags("number_of_statements", text)).toBe("2")
  })
})
