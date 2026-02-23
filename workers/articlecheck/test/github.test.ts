import { describe, it, expect } from "vitest"
import {
  parseReviewers,
  isArticleCheckCommand,
  isPullRequestComment
} from "../src/github"
import type { WebhookPayload } from "../src/types"

describe("parseReviewers", () => {
  it("parses a valid JSON array of strings", () => {
    const result = parseReviewers('["alice","bob","charlie"]')
    expect(result).toEqual(["alice", "bob", "charlie"])
  })

  it("returns empty array for invalid JSON", () => {
    const result = parseReviewers("not-json")
    expect(result).toEqual([])
  })

  it("returns empty array for empty string", () => {
    const result = parseReviewers("")
    expect(result).toEqual([])
  })

  it("filters out non-string values", () => {
    const result = parseReviewers('["alice", 42, null, "bob"]')
    expect(result).toEqual(["alice", "bob"])
  })

  it("returns empty array for a JSON object", () => {
    const result = parseReviewers('{"user": "alice"}')
    expect(result).toEqual([])
  })
})

describe("isArticleCheckCommand", () => {
  it("recognizes /articlecheck command", () => {
    expect(isArticleCheckCommand("/articlecheck")).toBe(true)
  })

  it("recognizes /articlecheck with trailing text", () => {
    expect(isArticleCheckCommand("/articlecheck please")).toBe(true)
  })

  it("recognizes /articlecheck with leading whitespace", () => {
    expect(isArticleCheckCommand("  /articlecheck")).toBe(true)
  })

  it("rejects unrelated comments", () => {
    expect(isArticleCheckCommand("looks good to me")).toBe(false)
  })

  it("rejects comments mentioning articlecheck mid-sentence", () => {
    expect(isArticleCheckCommand("please run /articlecheck")).toBe(false)
  })

  it("rejects empty string", () => {
    expect(isArticleCheckCommand("")).toBe(false)
  })
})

describe("isPullRequestComment", () => {
  it("returns true when pull_request is present", () => {
    const payload = {
      issue: {
        number: 1,
        pull_request: {
          url: "https://api.github.com/repos/test/test/pulls/1"
        }
      }
    } as WebhookPayload

    expect(isPullRequestComment(payload)).toBe(true)
  })

  it("returns false when pull_request is absent", () => {
    const payload = {
      issue: {
        number: 1
      }
    } as WebhookPayload

    expect(isPullRequestComment(payload)).toBe(false)
  })
})
