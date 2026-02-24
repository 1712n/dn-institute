import { describe, it, expect } from "vitest";
import { parseDiff } from "../src/github";

describe("parseDiff", () => {
  it("extracts added lines from content/*.md files", () => {
    const raw = `diff --git a/content/attacks/2024-01-01-test.md b/content/attacks/2024-01-01-test.md
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/content/attacks/2024-01-01-test.md
@@ -0,0 +1,5 @@
+---
+title: "Test Attack"
+date: 2024-01-01
+---
+## Summary`;

    const files = parseDiff(raw);
    expect(files).toHaveLength(1);
    expect(files[0].filename).toBe("content/attacks/2024-01-01-test.md");
    expect(files[0].content).toContain("title: \"Test Attack\"");
    expect(files[0].content).toContain("## Summary");
  });

  it("ignores non-markdown and non-content files", () => {
    const raw = `diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,1 +1,2 @@
+New line in readme
diff --git a/tools/script.py b/tools/script.py
--- a/tools/script.py
+++ b/tools/script.py
@@ -1,1 +1,2 @@
+print("hello")`;

    const files = parseDiff(raw);
    expect(files).toHaveLength(0);
  });

  it("returns empty array for empty diff", () => {
    expect(parseDiff("")).toHaveLength(0);
  });

  it("handles multiple content files", () => {
    const raw = `diff --git a/content/attacks/a.md b/content/attacks/a.md
--- /dev/null
+++ b/content/attacks/a.md
@@ -0,0 +1,1 @@
+File A
diff --git a/content/attacks/b.md b/content/attacks/b.md
--- /dev/null
+++ b/content/attacks/b.md
@@ -0,0 +1,1 @@
+File B`;

    const files = parseDiff(raw);
    expect(files).toHaveLength(2);
    expect(files[0].content).toBe("File A");
    expect(files[1].content).toBe("File B");
  });
});

describe("verifyWebhookSignature (import check)", () => {
  it("module exports exist", async () => {
    const mod = await import("../src/crypto");
    expect(typeof mod.verifyWebhookSignature).toBe("function");
  });
});

describe("braveSearch (import check)", () => {
  it("module exports exist", async () => {
    const mod = await import("../src/search");
    expect(typeof mod.braveSearch).toBe("function");
  });
});

describe("callClaude (import check)", () => {
  it("module exports exist", async () => {
    const mod = await import("../src/llm");
    expect(typeof mod.callClaude).toBe("function");
  });
});

describe("pipeline (import check)", () => {
  it("module exports exist", async () => {
    const mod = await import("../src/pipeline");
    expect(typeof mod.runArticleCheck).toBe("function");
  });
});
