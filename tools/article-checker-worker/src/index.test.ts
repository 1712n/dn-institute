import { describe, it, expect, vi, beforeEach } from "vitest"
import {
  verifyWebhookSignature,
  parseDiff,
  removePlus,
} from "./github"
import { extractBetweenTags } from "./claude"

// ─── Unit Tests: Diff Parsing ───────────────────────────────────────

describe("parseDiff", () => {
  it("parses a unified diff into structured files", () => {
    const diff = `diff --git a/content/attacks/2023-09-15-Remitano.md b/content/attacks/2023-09-15-Remitano.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/2023-09-15-Remitano.md
@@ -0,0 +1,50 @@
+---
+date: 2023-09-14
+target-entities: Remitano
+---
+
+## Summary
+Remitano was hacked.
`

    const files = parseDiff(diff)
    expect(files).toHaveLength(1)
    expect(files[0].header).toContain("Remitano.md")
    expect(files[0].body).toHaveLength(1)
    expect(files[0].body[0].body).toContain("Remitano")
  })

  it("handles multiple files in diff", () => {
    const diff = `diff --git a/file1.md b/file1.md
--- a/file1.md
+++ b/file1.md
@@ -1,3 +1,3 @@
+content1
diff --git a/file2.md b/file2.md
--- a/file2.md
+++ b/file2.md
@@ -1,3 +1,3 @@
+content2
`

    const files = parseDiff(diff)
    expect(files).toHaveLength(2)
  })

  it("returns empty array for empty diff", () => {
    const files = parseDiff("")
    expect(files).toHaveLength(0)
  })
})

// ─── Unit Tests: removePlus ─────────────────────────────────────────

describe("removePlus", () => {
  it("removes leading + from lines", () => {
    const input = "+line1\n+line2\n line3"
    const result = removePlus(input)
    expect(result).toBe("line1\nline2\n line3")
  })

  it("handles lines without +", () => {
    const input = "line1\nline2"
    const result = removePlus(input)
    expect(result).toBe("line1\nline2")
  })

  it("only removes the first +", () => {
    const input = "+a + b"
    const result = removePlus(input)
    expect(result).toBe("a + b")
  })
})

// ─── Unit Tests: extractBetweenTags ─────────────────────────────────

describe("extractBetweenTags", () => {
  it("extracts text between tags", () => {
    const text = "<answer>Hello World</answer>"
    expect(extractBetweenTags("answer", text)).toBe("Hello World")
  })

  it("returns last match when multiple tags exist", () => {
    const text = "<tag>first</tag> <tag>second</tag>"
    expect(extractBetweenTags("tag", text)).toBe("second")
  })

  it("returns null when tag not found", () => {
    const text = "no tags here"
    expect(extractBetweenTags("answer", text)).toBeNull()
  })

  it("handles multiline content", () => {
    const text = "<answer>\nline1\nline2\n</answer>"
    expect(extractBetweenTags("answer", text)).toBe("line1\nline2")
  })

  it("strips whitespace by default", () => {
    const text = "<tag>  spaced  </tag>"
    expect(extractBetweenTags("tag", text)).toBe("spaced")
  })

  it("preserves whitespace when strip is false", () => {
    const text = "<tag>  spaced  </tag>"
    expect(extractBetweenTags("tag", text, false)).toBe("  spaced  ")
  })

  it("extracts number_of_statements", () => {
    const text =
      "<statement>fact1</statement><number_of_statements>3</number_of_statements>"
    expect(extractBetweenTags("number_of_statements", text)).toBe("3")
  })
})

// ─── Unit Tests: Webhook Signature Verification ──────────────────────

describe("verifyWebhookSignature", () => {
  it("returns false for null signature", async () => {
    const result = await verifyWebhookSignature("payload", null, "secret")
    expect(result).toBe(false)
  })

  it("returns false for signature without sha256= prefix", async () => {
    const result = await verifyWebhookSignature("payload", "invalid", "secret")
    expect(result).toBe(false)
  })

  it("verifies a correct signature", async () => {
    const secret = "test-secret"
    const payload = '{"test": true}'

    // Generate a valid signature
    const encoder = new TextEncoder()
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    )
    const sig = await crypto.subtle.sign("HMAC", key, encoder.encode(payload))
    const hex = Array.from(new Uint8Array(sig))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")

    const result = await verifyWebhookSignature(
      payload,
      `sha256=${hex}`,
      secret
    )
    expect(result).toBe(true)
  })

  it("rejects an incorrect signature", async () => {
    const result = await verifyWebhookSignature(
      "payload",
      "sha256=0000000000000000000000000000000000000000000000000000000000000000",
      "secret"
    )
    expect(result).toBe(false)
  })
})
