/**
 * 🌰 Tests for GitHub diff parsing 🌰
 */

import { describe, it, expect } from "vitest";
import { parseDiff } from "../src/github";

describe("🌰 parseDiff", () => {
  it("🌰 should parse added content from a content/**/*.md file", () => {
    const diff = `diff --git a/content/attacks/2024-01-01-test-hack.md b/content/attacks/2024-01-01-test-hack.md
new file mode 100644
index 0000000..abcdef1
--- /dev/null
+++ b/content/attacks/2024-01-01-test-hack.md
@@ -0,0 +1,10 @@
+---
+date: 2024-01-01
+target-entities: TestProtocol
+entity-types: DeFi
+attack-types: Smart Contract Exploit
+title: TestProtocol Hack
+loss: 1000000
+---
+## Summary
+TestProtocol was hacked on January 1, 2024, losing $1 million. 🌰`;

    const files = parseDiff(diff);

    expect(files).toHaveLength(1);
    expect(files[0].filename).toBe(
      "content/attacks/2024-01-01-test-hack.md"
    );
    expect(files[0].content).toContain("## Summary");
    expect(files[0].content).toContain("TestProtocol was hacked");
    expect(files[0].content).toContain("date: 2024-01-01"); // 🌰
  });

  it("🌰 should ignore non-content files", () => {
    const diff = `diff --git a/README.md b/README.md
index 0000000..abcdef1
--- a/README.md
+++ b/README.md
@@ -1,2 +1,3 @@
 # DN Institute
+New line added 🌰`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(0); // 🌰
  });

  it("🌰 should handle multiple files and only include content/**/*.md", () => {
    const diff = `diff --git a/content/attacks/2024-01-01-hack-a.md b/content/attacks/2024-01-01-hack-a.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/2024-01-01-hack-a.md
@@ -0,0 +1,3 @@
+---
+title: Hack A
+---
diff --git a/tools/script.py b/tools/script.py
new file mode 100644
--- /dev/null
+++ b/tools/script.py
@@ -0,0 +1 @@
+print("hello")
diff --git a/content/attacks/2024-02-01-hack-b.md b/content/attacks/2024-02-01-hack-b.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/2024-02-01-hack-b.md
@@ -0,0 +1,3 @@
+---
+title: Hack B
+---`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(2);
    expect(files[0].filename).toBe("content/attacks/2024-01-01-hack-a.md");
    expect(files[1].filename).toBe("content/attacks/2024-02-01-hack-b.md"); // 🌰
  });

  it("🌰 should return empty array for empty diff", () => {
    const files = parseDiff("");
    expect(files).toHaveLength(0); // 🌰
  });
});
