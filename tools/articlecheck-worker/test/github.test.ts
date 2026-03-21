import { describe, it, expect } from "vitest";
import {
  parseDiff,
  removePlus,
  isAllowedReviewer,
  extractArticleText,
} from "../src/github";
import { extractBetweenTags } from "../src/pipeline";

// ─── isAllowedReviewer ──────────────────────────────────────────────────────

describe("isAllowedReviewer", () => {
  it("returns true for allowed user", () => {
    expect(isAllowedReviewer("alice", '["alice","bob"]')).toBe(true);
  });

  it("returns false for disallowed user", () => {
    expect(isAllowedReviewer("eve", '["alice","bob"]')).toBe(false);
  });

  it("returns false on invalid JSON", () => {
    expect(isAllowedReviewer("alice", "not-json")).toBe(false);
  });

  it("returns false on empty list", () => {
    expect(isAllowedReviewer("alice", "[]")).toBe(false);
  });

  it("is case-sensitive (GitHub usernames are case-sensitive)", () => {
    expect(isAllowedReviewer("Alice", '["alice"]')).toBe(false);
  });

  it("handles single-element array", () => {
    expect(isAllowedReviewer("solo", '["solo"]')).toBe(true);
  });

  it("handles empty string actor", () => {
    expect(isAllowedReviewer("", '["alice"]')).toBe(false);
  });

  it("handles empty string reviewers", () => {
    expect(isAllowedReviewer("alice", "")).toBe(false);
  });
});

// ─── parseDiff ──────────────────────────────────────────────────────────────

describe("parseDiff", () => {
  const REALISTIC_DIFF = `diff --git a/content/attacks/2024-01-15-TestExchange.md b/content/attacks/2024-01-15-TestExchange.md
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/content/attacks/2024-01-15-TestExchange.md
@@ -0,0 +1,30 @@
+---
+date: 2024-01-15
+target-entities: TestExchange
+entity-types:
+  - Exchange
+attack-types:
+  - Smart Contract Exploit
+title: "TestExchange Exploit"
+loss: 5000000
+---
+
+## Summary
+On January 15, 2024, TestExchange was exploited for $5 million.`;

  it("parses a realistic article diff", () => {
    const files = parseDiff(REALISTIC_DIFF);
    expect(files).toHaveLength(1);
    expect(files[0]!.header).toContain(
      "content/attacks/2024-01-15-TestExchange.md"
    );
    expect(files[0]!.bodySegments).toHaveLength(1);
    expect(files[0]!.bodySegments[0]!.body).toContain(
      "target-entities: TestExchange"
    );
    expect(files[0]!.bodySegments[0]!.body).toContain("## Summary");
  });

  it("returns empty for empty diff", () => {
    expect(parseDiff("")).toEqual([]);
  });

  it("returns empty for whitespace-only diff", () => {
    expect(parseDiff("   \n  \n")).toEqual([]);
  });

  it("handles multiple files", () => {
    const diff = `diff --git a/file1.md b/file1.md
--- a/file1.md
+++ b/file1.md
@@ -1 +1 @@
-old
+new
diff --git a/file2.md b/file2.md
--- a/file2.md
+++ b/file2.md
@@ -1 +1 @@
-old2
+new2`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(2);
  });

  it("handles multiple hunks in a single file", () => {
    const diff = `diff --git a/file.md b/file.md
--- a/file.md
+++ b/file.md
@@ -1,3 +1,3 @@
 unchanged
-old1
+new1
@@ -10,3 +10,3 @@
 unchanged2
-old2
+new2`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(1);
    expect(files[0]!.bodySegments).toHaveLength(2);
  });

  it("handles binary file diffs gracefully", () => {
    const diff = `diff --git a/image.png b/image.png
new file mode 100644
index 0000000..abc1234
Binary files /dev/null and b/image.png differ`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(1);
    // No @@ markers means no body segments
    expect(files[0]!.bodySegments).toHaveLength(0);
  });

  it("handles rename diffs", () => {
    const diff = `diff --git a/old-name.md b/new-name.md
similarity index 100%
rename from old-name.md
rename to new-name.md`;

    const files = parseDiff(diff);
    expect(files).toHaveLength(1);
    expect(files[0]!.header).toContain("old-name.md");
  });
});

// ─── extractArticleText ─────────────────────────────────────────────────────

describe("extractArticleText", () => {
  it("returns null for empty file list", () => {
    expect(extractArticleText([])).toBeNull();
  });

  it("returns header when no body segments", () => {
    expect(
      extractArticleText([{ header: "header", bodySegments: [] }])
    ).toBe("header");
  });

  it("extracts first file, first hunk only (matching Python behavior)", () => {
    const files = [
      {
        header: "HEADER\n",
        bodySegments: [
          { header: " -0,0 +1,5 ", body: "+line1\n+line2" },
          { header: " -5,0 +5,5 ", body: "+line3\n+line4" },
        ],
      },
    ];
    const text = extractArticleText(files);
    expect(text).toContain("HEADER");
    expect(text).toContain("line1");
    expect(text).toContain("line2");
    // Must NOT include second hunk — Python: diff[0]['body'][0]['body']
    expect(text).not.toContain("line3");
    expect(text).not.toContain("line4");
  });

  it("only uses first file when multiple files present", () => {
    const files = [
      {
        header: "FILE1\n",
        bodySegments: [{ header: " hdr ", body: "+first file content" }],
      },
      {
        header: "FILE2\n",
        bodySegments: [{ header: " hdr ", body: "+second file content" }],
      },
    ];
    const text = extractArticleText(files);
    expect(text).toContain("first file content");
    expect(text).not.toContain("second file content");
  });

  it("strips + markers from added lines", () => {
    const files = [
      {
        header: "H\n",
        bodySegments: [
          { header: " h ", body: "+added line\n context line\n-removed line" },
        ],
      },
    ];
    const text = extractArticleText(files);
    expect(text).toContain("added line");
    expect(text).not.toContain("+added line");
  });
});

// ─── removePlus ─────────────────────────────────────────────────────────────

describe("removePlus", () => {
  it("strips leading + from diff lines", () => {
    expect(removePlus("+line1\n+line2\nline3")).toBe("line1\nline2\nline3");
  });

  it("leaves non-plus lines unchanged", () => {
    expect(removePlus("no plus here")).toBe("no plus here");
  });

  it("handles empty string", () => {
    expect(removePlus("")).toBe("");
  });

  it("only strips first + character per line", () => {
    expect(removePlus("+a + b")).toBe("a + b");
  });

  it("preserves lines starting with ++", () => {
    // ++ lines in diffs are file markers — removePlus strips one +, leaving +
    expect(removePlus("+++ b/file.md")).toBe("++ b/file.md");
  });

  it("handles lines that are just +", () => {
    expect(removePlus("+")).toBe("");
  });
});

// ─── extractBetweenTags ─────────────────────────────────────────────────────

describe("extractBetweenTags", () => {
  it("extracts content between tags", () => {
    expect(extractBetweenTags("tag", "<tag>hello</tag>")).toBe("hello");
  });

  it("returns last match when multiple", () => {
    expect(
      extractBetweenTags("tag", "<tag>first</tag> <tag>second</tag>")
    ).toBe("second");
  });

  it("returns null when no match", () => {
    expect(extractBetweenTags("tag", "no tags here")).toBeNull();
  });

  it("handles multiline content", () => {
    expect(
      extractBetweenTags("answer", "<answer>line1\nline2\nline3</answer>")
    ).toBe("line1\nline2\nline3");
  });

  it("extracts number_of_statements", () => {
    const text =
      "<statement>S1</statement><number_of_statements>3</number_of_statements>";
    expect(extractBetweenTags("number_of_statements", text)).toBe("3");
  });

  it("handles tags with trailing space", () => {
    expect(extractBetweenTags("tag", "<tag >hello</tag >")).toBe("hello");
  });

  it("strips whitespace from extracted content", () => {
    expect(extractBetweenTags("tag", "<tag>  spaced  </tag>")).toBe("spaced");
  });

  it("handles nested tags of different types", () => {
    const text =
      "<outer><inner>nested</inner></outer>";
    expect(extractBetweenTags("outer", text)).toBe(
      "<inner>nested</inner>"
    );
    expect(extractBetweenTags("inner", text)).toBe("nested");
  });

  it("handles empty tags", () => {
    // The regex requires .+? (one or more chars) so empty tags return null
    expect(extractBetweenTags("tag", "<tag></tag>")).toBeNull();
  });

  it("handles verdict tags from fact-checking output", () => {
    const factCheckOutput = `<statement>Hack was $5M</statement>
<verdict>True</verdict>
<source>https://example.com</source>`;
    expect(extractBetweenTags("verdict", factCheckOutput)).toBe("True");
    expect(extractBetweenTags("source", factCheckOutput)).toBe(
      "https://example.com"
    );
  });

  it("handles search_query extraction mid-stream", () => {
    // This is exactly how it's used in Phase 2 — partial completion ends with
    // <search_query>some query  (no closing tag — we append it)
    const partial = 'Let me search for this. <search_query>SampleDeFi exploit 2024';
    const withClose = partial + "</search_query>";
    expect(extractBetweenTags("search_query", withClose)).toBe(
      "SampleDeFi exploit 2024"
    );
  });
});
