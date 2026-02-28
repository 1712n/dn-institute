/**
 * 🌰 Tests for GitHub API interactions
 */

import { describe, it, expect } from "vitest"
import {
  isAllowedReviewer,
  validateWebhookPayload,
  parseDiff,
} from "../src/github"
import type { GitHubWebhookPayload } from "../src/types"

// ─── isAllowedReviewer ──────────────────────────────────────────────────────

describe("isAllowedReviewer", () => {
  it("should allow default reviewer (evgenydmitriev)", () => {
    expect(isAllowedReviewer("evgenydmitriev")).toBe(true)
  })

  it("should reject unknown user with no allowlist", () => {
    expect(isAllowedReviewer("randomuser")).toBe(false)
  })

  it("should check custom allowlist from JSON", () => {
    const allowlist = '["alice","bob","charlie"]'
    expect(isAllowedReviewer("bob", allowlist)).toBe(true)
    expect(isAllowedReviewer("dave", allowlist)).toBe(false)
  })

  it("should fall back to defaults on invalid JSON", () => {
    expect(isAllowedReviewer("evgenydmitriev", "not-json")).toBe(true)
    expect(isAllowedReviewer("randomuser", "not-json")).toBe(false)
  })

  it("should fall back to defaults on non-array JSON", () => {
    expect(isAllowedReviewer("evgenydmitriev", '{"key":"value"}')).toBe(true)
  })
})

// ─── validateWebhookPayload ─────────────────────────────────────────────────

describe("validateWebhookPayload", () => {
  function makePayload(overrides?: Partial<GitHubWebhookPayload>): GitHubWebhookPayload {
    return {
      action: "created",
      issue: {
        number: 42,
        pull_request: { url: "https://api.github.com/repos/owner/repo/pulls/42" },
      },
      comment: {
        id: 123,
        body: "Please run /articlecheck on this PR",
        user: { login: "reviewer1" },
      },
      repository: {
        full_name: "owner/repo",
        owner: { login: "owner" },
        name: "repo",
      },
      sender: { login: "reviewer1" },
      ...overrides,
    }
  }

  it("should validate a correct /articlecheck payload", () => {
    const result = validateWebhookPayload(makePayload())
    expect(result.valid).toBe(true)
    if (result.valid) {
      expect(result.prNumber).toBe(42)
    }
  })

  it("should reject non-created actions", () => {
    const result = validateWebhookPayload(makePayload({ action: "deleted" }))
    expect(result.valid).toBe(false)
  })

  it("should reject comments not on PRs", () => {
    const result = validateWebhookPayload(
      makePayload({ issue: { number: 42 } })
    )
    expect(result.valid).toBe(false)
  })

  it("should reject comments without /articlecheck", () => {
    const result = validateWebhookPayload(
      makePayload({
        comment: {
          id: 123,
          body: "LGTM!",
          user: { login: "reviewer1" },
        },
      })
    )
    expect(result.valid).toBe(false)
  })
})

// ─── parseDiff ──────────────────────────────────────────────────────────────

describe("parseDiff", () => {
  it("should parse added lines from a unified diff", () => {
    const diff = `diff --git a/content/attacks/2024-01-01-test.md b/content/attacks/2024-01-01-test.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/2024-01-01-test.md
@@ -0,0 +1,10 @@
+---
+date: 2024-01-01
+title: Test Attack
+---
+
+## Summary
+
+A test attack occurred.
`

    const files = parseDiff(diff)
    expect(files.length).toBe(1)
    expect(files[0].filename).toBe("content/attacks/2024-01-01-test.md")
    expect(files[0].body).toContain("## Summary")
    expect(files[0].body).toContain("A test attack occurred.")
  })

  it("should skip non-markdown files", () => {
    const diff = `diff --git a/config.json b/config.json
--- a/config.json
+++ b/config.json
@@ -1 +1,2 @@
+{"key": "value"}
`

    const files = parseDiff(diff)
    expect(files.length).toBe(0)
  })

  it("should handle multiple files", () => {
    const diff = `diff --git a/content/a.md b/content/a.md
--- /dev/null
+++ b/content/a.md
@@ -0,0 +1,2 @@
+# File A
+Content A
diff --git a/content/b.md b/content/b.md
--- /dev/null
+++ b/content/b.md
@@ -0,0 +1,2 @@
+# File B
+Content B
`

    const files = parseDiff(diff)
    expect(files.length).toBe(2)
    expect(files[0].filename).toBe("content/a.md")
    expect(files[1].filename).toBe("content/b.md")
  })

  it("should return empty array for empty diff", () => {
    expect(parseDiff("")).toEqual([])
  })

  it("should only extract added lines (not context or removed)", () => {
    const diff = `diff --git a/content/test.md b/content/test.md
--- a/content/test.md
+++ b/content/test.md
@@ -1,3 +1,4 @@
 existing line
-removed line
+added line
+another added line
 context line
`

    const files = parseDiff(diff)
    expect(files.length).toBe(1)
    expect(files[0].body).toContain("added line")
    expect(files[0].body).toContain("another added line")
    expect(files[0].body).not.toContain("removed line")
    expect(files[0].body).not.toContain("existing line")
  })
})
