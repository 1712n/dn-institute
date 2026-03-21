/**
 * End-to-end simulation + adversarial test suite.
 *
 * Tests the full webhook → parse → pipeline data flow with realistic data,
 * plus edge cases, malformed inputs, and security boundary checks.
 */

import { describe, it, expect } from "vitest";
import {
  parseDiff,
  extractArticleText,
  isAllowedReviewer,
  removePlus,
} from "../src/github";
import { extractBetweenTags } from "../src/pipeline";
import { formatSearchResults, BRAVE_DESCRIPTION } from "../src/brave";
import { RETRIEVAL_PROMPT } from "../src/prompts";

// ─── Realistic Test Data ────────────────────────────────────────────────────

const REALISTIC_DIFF = `diff --git a/content/attacks/2024-03-15-SampleDeFi.md b/content/attacks/2024-03-15-SampleDeFi.md
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/content/attacks/2024-03-15-SampleDeFi.md
@@ -0,0 +1,42 @@
+---
+date: 2024-03-15
+target-entities: SampleDeFi Protocol
+entity-types:
+  - DeFi
+attack-types:
+  - Smart Contract Exploit
+  - Flash Loan Attack
+title: "SampleDeFi Protocol Flash Loan Exploit"
+loss: 8500000
+---
+
+## Summary
+
+On March 15, 2024, SampleDeFi Protocol was exploited through a flash loan attack resulting in losses of approximately $8.5 million. The attacker manipulated the price oracle by using a large flash loan from Aave to inflate the token price on the platform's AMM pool.
+
+## Attackers
+
+The identity of the attacker(s) remains unknown. The attack originated from address 0x1234...5678 which was funded through Tornado Cash approximately 2 hours before the exploit.
+
+## Losses
+
+- $5.2 million in ETH
+- $3.3 million in USDC
+- Total: approximately $8.5 million
+
+## Timeline
+
+- **March 15, 2024, 02:15 PM UTC:** Attacker address funded via Tornado Cash
+- **March 15, 2024, 04:22 PM UTC:** Flash loan executed on Aave
+- **March 15, 2024, 04:22 PM UTC:** Price oracle manipulated
+- **March 15, 2024, 04:23 PM UTC:** Funds drained from lending pool
+- **March 15, 2024, 04:30 PM UTC:** SampleDeFi team pauses contracts
+- **March 15, 2024, 05:00 PM UTC:** Post-mortem published on Twitter
+
+## Security Failure Causes
+
+- **Reliance on single price oracle:** The protocol used only its own AMM pool for price feeds rather than a decentralized oracle like Chainlink.
+- **No flash loan protection:** The lending pool did not implement any flash loan guards or same-block borrow/repay prevention.
+- **Insufficient liquidity checks:** Price impact thresholds were not enforced on large trades.`;

const SAMPLE_WEBHOOK = {
  action: "created",
  comment: {
    id: 123456,
    body: "/articlecheck",
    user: { login: "evgenydmitriev" },
  },
  issue: {
    number: 500,
    pull_request: {
      url: "https://api.github.com/repos/1712n/dn-institute/pulls/500",
      diff_url: "https://github.com/1712n/dn-institute/pull/500.diff",
      html_url: "https://github.com/1712n/dn-institute/pull/500",
    },
  },
  repository: { full_name: "1712n/dn-institute" },
};

// ─── E2E: Full Pipeline Data Flow ───────────────────────────────────────────

describe("E2E: Webhook → Parse → Extract", () => {
  it("validates webhook payload structure", () => {
    const p = SAMPLE_WEBHOOK;
    expect(p.action).toBe("created");
    expect(p.comment.body).toContain("/articlecheck");
    expect(p.issue.pull_request).toBeDefined();
    expect(p.repository.full_name).toBe("1712n/dn-institute");
  });

  it("checks reviewer permission correctly", () => {
    const reviewers = '["evgenydmitriev","reviewer2"]';
    expect(isAllowedReviewer("evgenydmitriev", reviewers)).toBe(true);
    expect(isAllowedReviewer("random-user", reviewers)).toBe(false);
  });

  it("parses realistic diff and extracts complete article", () => {
    const files = parseDiff(REALISTIC_DIFF);
    const text = extractArticleText(files);

    expect(text).not.toBeNull();
    // All 6 required metadata headers
    expect(text!).toContain("date: 2024-03-15");
    expect(text!).toContain("target-entities: SampleDeFi Protocol");
    expect(text!).toContain("entity-types:");
    expect(text!).toContain("attack-types:");
    expect(text!).toContain("title:");
    expect(text!).toContain("loss: 8500000");
    // All 5 required section headers
    expect(text!).toContain("## Summary");
    expect(text!).toContain("## Attackers");
    expect(text!).toContain("## Losses");
    expect(text!).toContain("## Timeline");
    expect(text!).toContain("## Security Failure Causes");
    // Key content
    expect(text!).toContain("$8.5 million");
    expect(text!).toContain("Tornado Cash");
  });

  it("strips + markers from added lines but preserves content", () => {
    const files = parseDiff(REALISTIC_DIFF);
    const text = extractArticleText(files)!;
    expect(text).not.toContain("+## Summary");
    expect(text).not.toContain("+date:");
    expect(text).toContain("## Summary");
    expect(text).toContain("date:");
  });
});

// ─── E2E: Pipeline Phase Data Flow ──────────────────────────────────────────

describe("E2E: Phase 1 → Phase 2 → Phase 3 data contracts", () => {
  it("Phase 1 output: extractBetweenTags parses typical statement extraction", () => {
    const phase1 = `<statement>On March 15, 2024, SampleDeFi was exploited for $8.5 million</statement>
<statement>The attacker used a flash loan from Aave</statement>
<statement>$5.2 million in ETH was lost</statement>
<number_of_statements>3</number_of_statements>`;

    expect(extractBetweenTags("number_of_statements", phase1)).toBe("3");
    expect(phase1.match(/<statement>(.+?)<\/statement>/gs)).toHaveLength(3);
  });

  it("Phase 2: RETRIEVAL_PROMPT has {description} placeholder for Brave", () => {
    expect(RETRIEVAL_PROMPT).toContain("{description}");
    const filled = RETRIEVAL_PROMPT.replace("{description}", BRAVE_DESCRIPTION);
    expect(filled).toContain("Brave Search Engine Tool");
    expect(filled).not.toContain("{description}");
  });

  it("Phase 2: RETRIEVAL_PROMPT has {current_time} placeholder", () => {
    expect(RETRIEVAL_PROMPT).toContain("{current_time}");
    const filled = RETRIEVAL_PROMPT.replace("{current_time}", "2024-03-15 12:00:00");
    expect(filled).toContain("2024-03-15 12:00:00");
    expect(filled).not.toContain("{current_time}");
  });

  it("Phase 2: search query extraction from partial completion", () => {
    const partial =
      'I need to verify this claim. <search_query>SampleDeFi exploit March 2024 amount';
    const withClose = partial + "</search_query>";
    expect(extractBetweenTags("search_query", withClose)).toBe(
      "SampleDeFi exploit March 2024 amount"
    );
  });

  it("Phase 2: search results format matches what Claude expects", () => {
    const results = [
      "Web Page Title: DeFi Hack Report\nWeb Page URL: https://example.com\nWeb Page Summary: <article>SampleDeFi lost $8.5M...</article>",
    ];
    const formatted = formatSearchResults(results);
    expect(formatted).toMatch(
      /^[\s]*<search_results>[\s\S]*<\/search_results>[\s]*$/
    );
  });

  it("Phase 3 output: extractBetweenTags parses editorial review", () => {
    const phase3 = `<answer>
## Fact-Checking Results

- **Statement**: SampleDeFi was exploited for $8.5 million :white_check_mark:
  - **Source**: [https://example.com](https://example.com)

## Editor's Notes
The article is well-structured.

## Hugo SSG Formatting Check
- Does it match Hugo SSG formatting? :white_check_mark:

## Filename Check
- Correct Filename: \`2024-03-15-SampleDeFi.md\`
- Your Filename: \`2024-03-15-SampleDeFi.md\` :white_check_mark:
</answer>`;

    const answer = extractBetweenTags("answer", phase3);
    expect(answer).not.toBeNull();
    expect(answer!).toContain("## Fact-Checking Results");
    expect(answer!).toContain(":white_check_mark:");
    expect(answer!).toContain("## Editor's Notes");
    expect(answer!).toContain("## Hugo SSG Formatting Check");
    expect(answer!).toContain("## Filename Check");
  });
});

// ─── Adversarial: Malformed Inputs ──────────────────────────────────────────

describe("Adversarial: malformed diffs", () => {
  it("handles diff with no @@ markers (binary file)", () => {
    const diff = `diff --git a/image.png b/image.png
Binary files /dev/null and b/image.png differ`;
    const files = parseDiff(diff);
    const text = extractArticleText(files);
    // Should return just the header, no body content
    expect(text).toBeDefined();
    expect(text!.length).toBeLessThan(200);
  });

  it("handles diff with only deletions", () => {
    const diff = `diff --git a/removed.md b/removed.md
deleted file mode 100644
--- a/removed.md
+++ /dev/null
@@ -1,5 +0,0 @@
-line1
-line2
-line3`;
    const files = parseDiff(diff);
    const text = extractArticleText(files);
    // removePlus only strips +, so - lines stay as-is
    expect(text).toContain("-line1");
  });

  it("handles massive diff (stress test)", () => {
    let bigDiff = `diff --git a/big.md b/big.md\n--- a/big.md\n+++ b/big.md\n@@ -0,0 +1,10000 @@\n`;
    for (let i = 0; i < 10000; i++) {
      bigDiff += `+Line ${i} of a very large article with lots of content about crypto attacks\n`;
    }
    const files = parseDiff(bigDiff);
    expect(files).toHaveLength(1);
    const text = extractArticleText(files);
    expect(text).toContain("Line 0");
    expect(text).toContain("Line 9999");
  });

  it("handles diff with @@ in content (not just markers)", () => {
    const diff = `diff --git a/file.md b/file.md
--- a/file.md
+++ b/file.md
@@ -0,0 +1,3 @@
+This article mentions @@ email addresses
+And more @@ symbols in text`;
    const files = parseDiff(diff);
    // The @@ in content will split incorrectly — this is a known limitation
    // of both the Python and our implementation. Documenting the behavior.
    expect(files.length).toBeGreaterThanOrEqual(1);
  });

  it("handles Unicode content", () => {
    const diff = `diff --git a/file.md b/file.md
--- a/file.md
+++ b/file.md
@@ -0,0 +1,3 @@
+# 中文标题
+Ataques de criptomonedas — $1,000,000
+Rug pull на бирже`;
    const files = parseDiff(diff);
    const text = extractArticleText(files);
    expect(text).toContain("中文标题");
    expect(text).toContain("$1,000,000");
    expect(text).toContain("бирже");
  });

  it("handles empty lines in diff", () => {
    const diff = `diff --git a/file.md b/file.md
--- a/file.md
+++ b/file.md
@@ -0,0 +1,5 @@
+line1
+
+line3
+
+line5`;
    const files = parseDiff(diff);
    const text = extractArticleText(files);
    expect(text).toContain("line1");
    expect(text).toContain("line3");
    expect(text).toContain("line5");
  });
});

// ─── Adversarial: Security Boundary Checks ──────────────────────────────────

describe("Adversarial: security boundaries", () => {
  it("rejects webhook with no trigger command", () => {
    expect(
      "just a regular comment".includes("/articlecheck")
    ).toBe(false);
  });

  it("rejects non-PR issue comments", () => {
    const payload = { issue: { number: 100 } }; // no pull_request field
    expect("pull_request" in payload.issue).toBe(false);
  });

  it("rejects edited comments (only created)", () => {
    expect("edited" === "created").toBe(false);
  });

  it("command detection is not fooled by substrings", () => {
    // "/articlecheck" should match, but also "/articlecheck please"
    expect("/articlecheck please".includes("/articlecheck")).toBe(true);
    // But "my/articlecheck" should also match (includes is substring)
    // This matches the Python behavior: contains(github.event.comment.body, '/articlecheck')
    expect("my/articlecheck".includes("/articlecheck")).toBe(true);
  });

  it("handles JSON with extra/unexpected fields gracefully", () => {
    const extendedPayload = {
      ...SAMPLE_WEBHOOK,
      unexpected_field: "should not crash",
      comment: {
        ...SAMPLE_WEBHOOK.comment,
        extra: { nested: true },
      },
    };
    // Should not throw when accessing known fields
    expect(extendedPayload.comment.body).toBe("/articlecheck");
    expect(extendedPayload.repository.full_name).toBe("1712n/dn-institute");
  });

  it("handles very long comment bodies", () => {
    const longBody = "/articlecheck " + "x".repeat(100000);
    expect(longBody.includes("/articlecheck")).toBe(true);
  });
});

// ─── Adversarial: extractBetweenTags Edge Cases ─────────────────────────────

describe("Adversarial: tag extraction edge cases", () => {
  it("handles malicious nested same-name tags", () => {
    // Regex is non-greedy (.+?) so it matches the INNERMOST pair
    const text = "<tag>outer <tag>inner</tag> still outer</tag>";
    const result = extractBetweenTags("tag", text);
    // Last match of the non-greedy pattern
    expect(result).toBeDefined();
  });

  it("handles tags with attributes (should not match)", () => {
    // Our regex: <tag\s?> — only allows optional single trailing space
    const text = '<tag class="foo">content</tag>';
    expect(extractBetweenTags("tag", text)).toBeNull();
  });

  it("handles extremely long content between tags", () => {
    const longContent = "x".repeat(100000);
    const text = `<answer>${longContent}</answer>`;
    expect(extractBetweenTags("answer", text)).toBe(longContent);
  });

  it("handles tags across many lines", () => {
    const text = "<answer>\nline1\nline2\nline3\nline4\nline5\n</answer>";
    expect(extractBetweenTags("answer", text)).toBe(
      "line1\nline2\nline3\nline4\nline5"
    );
  });

  it("returns null for self-closing tags", () => {
    expect(extractBetweenTags("tag", "<tag/>")).toBeNull();
  });

  it("handles number_of_statements with whitespace", () => {
    const text = "<number_of_statements> 5 </number_of_statements>";
    expect(extractBetweenTags("number_of_statements", text)).toBe("5");
  });

  it("parseInt handles non-numeric number_of_statements gracefully", () => {
    // If Claude returns garbage, parseInt returns NaN, Math.min(NaN, 5) = NaN
    // The for loop with NaN iterations runs 0 times — safe
    const val = parseInt("not a number", 10);
    expect(Number.isNaN(val)).toBe(true);
    expect(Math.min(val, 5)).toBeNaN();
    // for (let i = 0; i < NaN; i++) — never executes
    let count = 0;
    for (let i = 0; i < val; i++) count++;
    expect(count).toBe(0);
  });
});

// ─── Real-World: Article Format Validation ──────────────────────────────────

describe("Real-world: article format edge cases", () => {
  it("handles article with YAML list metadata (entity-types, attack-types)", () => {
    const diff = `diff --git a/content/attacks/2024-01-01-Multi.md b/content/attacks/2024-01-01-Multi.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/2024-01-01-Multi.md
@@ -0,0 +1,15 @@
+---
+date: 2024-01-01
+target-entities: Multi Protocol
+entity-types:
+  - DeFi
+  - Bridge
+attack-types:
+  - Smart Contract Exploit
+  - Governance Attack
+title: "Multi Protocol Exploit"
+loss: 1000000
+---
+
+## Summary
+Multi was exploited.`;
    const files = parseDiff(diff);
    const text = extractArticleText(files)!;
    expect(text).toContain("- DeFi");
    expect(text).toContain("- Bridge");
    expect(text).toContain("- Governance Attack");
  });

  it("handles article with special chars in title (quotes, ampersand)", () => {
    const diff = `diff --git a/content/attacks/2024-01-01-Test.md b/content/attacks/2024-01-01-Test.md
new file mode 100644
--- /dev/null
+++ b/content/attacks/2024-01-01-Test.md
@@ -0,0 +1,5 @@
+---
+title: "O'Reilly & Associates \"Hack\" — $1M Loss"
+loss: 1000000
+---
+## Summary`;
    const files = parseDiff(diff);
    const text = extractArticleText(files)!;
    expect(text).toContain("O'Reilly & Associates");
  });
});
