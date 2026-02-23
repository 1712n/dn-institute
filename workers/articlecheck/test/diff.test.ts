import { describe, it, expect } from "vitest"
import { parseDiff, removePlus } from "../src/diff"

describe("parseDiff", () => {
  it("extracts added content from article files", () => {
    const diff = `diff --git a/content/attacks/posts/2024-01-01-test.md b/content/attacks/posts/2024-01-01-test.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/posts/2024-01-01-test.md
@@ -0,0 +1,5 @@
+---
+title: Test Attack
+date: 2024-01-01
+---
+## Summary`

    const result = parseDiff(diff)
    expect(result).toHaveLength(1)
    expect(result[0]!.filename).toBe(
      "content/attacks/posts/2024-01-01-test.md"
    )
    expect(result[0]!.content).toContain("title: Test Attack")
    expect(result[0]!.content).toContain("## Summary")
  })

  it("ignores non-content files", () => {
    const diff = `diff --git a/workers/articlecheck/src/index.ts b/workers/articlecheck/src/index.ts
new file mode 100644
--- /dev/null
+++ b/workers/articlecheck/src/index.ts
@@ -0,0 +1 @@
+export default {}`

    const result = parseDiff(diff)
    expect(result).toHaveLength(0)
  })

  it("ignores non-markdown files in content directory", () => {
    const diff = `diff --git a/content/attacks/posts/image.png b/content/attacks/posts/image.png
new file mode 100644
Binary files /dev/null and b/content/attacks/posts/image.png differ`

    const result = parseDiff(diff)
    expect(result).toHaveLength(0)
  })

  it("handles multiple article files", () => {
    const diff = `diff --git a/content/attacks/posts/file1.md b/content/attacks/posts/file1.md
--- a/content/attacks/posts/file1.md
+++ b/content/attacks/posts/file1.md
@@ -1,2 +1,3 @@
 ## Summary
+Added line
diff --git a/content/attacks/posts/file2.md b/content/attacks/posts/file2.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/posts/file2.md
@@ -0,0 +1 @@
+## Summary of file 2`

    const result = parseDiff(diff)
    expect(result).toHaveLength(2)
    expect(result[0]!.filename).toBe("content/attacks/posts/file1.md")
    expect(result[1]!.filename).toBe("content/attacks/posts/file2.md")
  })

  it("returns empty array for empty diff", () => {
    expect(parseDiff("")).toEqual([])
  })
})

describe("removePlus", () => {
  it("removes leading + from lines", () => {
    const input = "+line one\n+line two\nline three"
    expect(removePlus(input)).toBe("line one\nline two\nline three")
  })

  it("handles text without plus signs", () => {
    const input = "line one\nline two"
    expect(removePlus(input)).toBe("line one\nline two")
  })
})
