import { describe, it, expect } from "vitest"
import { extractBetweenTags } from "../src/claude"

describe("extractBetweenTags", () => {
  it("extracts text between tags", () => {
    const text = "<answer>Hello world</answer>"
    expect(extractBetweenTags("answer", text)).toBe("Hello world")
  })

  it("returns the last match when multiple tags present", () => {
    const text =
      "<statement>First</statement> some text <statement>Second</statement>"
    expect(extractBetweenTags("statement", text)).toBe("Second")
  })

  it("returns null when tag not found", () => {
    const text = "No tags here"
    expect(extractBetweenTags("answer", text)).toBeNull()
  })

  it("handles multiline content", () => {
    const text = "<answer>\nLine 1\nLine 2\n</answer>"
    expect(extractBetweenTags("answer", text)).toBe("Line 1\nLine 2")
  })

  it("strips whitespace from extracted content", () => {
    const text = "<answer>  spaced  </answer>"
    expect(extractBetweenTags("answer", text)).toBe("spaced")
  })

  it("handles tags with trailing space", () => {
    const text = "<answer >content</answer >"
    expect(extractBetweenTags("answer", text)).toBe("content")
  })
})
