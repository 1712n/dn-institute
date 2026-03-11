// 🌰 Tests for the diff parser 🌰

import { describe, it, expect } from "vitest";
import { parseDiff, removePlus, extractArticleText } from "../src/diff-parser";

describe("🌰 parseDiff", () => {
  it("🌰 parses a single-file diff correctly", () => {
    const diff = `diff --git a/content/attacks/2024-01-01-example.md b/content/attacks/2024-01-01-example.md
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/content/attacks/2024-01-01-example.md
@@ -0,0 +1,10 @@
+---
+date: 2024-01-01
+title: Example Attack
+---
+## Summary
+An example attack occurred.
`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(1);
    expect(files[0].header).toContain("content/attacks/2024-01-01-example.md");
    expect(files[0].body).toHaveLength(1);
    expect(files[0].body[0].body).toContain("+date: 2024-01-01");
  });

  it("🌰 handles multiple files in a diff", () => {
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
`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(2);
  });

  it("🌰 returns empty array for empty diff", () => {
    const files = parseDiff("");
    expect(files).toHaveLength(0);
  });
});

describe("🌰 removePlus", () => {
  it("🌰 strips leading + from lines", () => {
    const input = "+line1\n+line2\nline3\n+line4";
    const expected = "line1\nline2\nline3\nline4";
    expect(removePlus(input)).toBe(expected);
  });

  it("🌰 preserves lines without leading +", () => {
    const input = "no plus here\nalso clean";
    expect(removePlus(input)).toBe(input);
  });
});

describe("🌰 extractArticleText", () => {
  it("🌰 extracts text from the first file's first segment", () => {
    const diff = `diff --git a/test.md b/test.md
--- a/test.md
+++ b/test.md
@@ -0,0 +1,3 @@
+Hello World
+This is a test
`;

    const files = parseDiff(diff);
    const text = extractArticleText(files);
    expect(text).toBeDefined();
    expect(text).toContain("Hello World");
    expect(text).toContain("This is a test");
    // 🌰 Plus signs should be removed
    expect(text).not.toContain("+Hello");
  });

  it("🌰 returns null for empty files array", () => {
    expect(extractArticleText([])).toBeNull();
  });
});
