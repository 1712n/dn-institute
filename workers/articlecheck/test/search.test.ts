/**
 * 🌰 Tests for search result formatting 🌰
 */

import { describe, it, expect } from "vitest";
import { formatSearchResults } from "../src/search";

describe("🌰 formatSearchResults", () => {
  it("🌰 should format results into XML structure", () => {
    const results = [
      {
        title: "Test Article",
        url: "https://example.com/article",
        description: "A test article about chestnuts 🌰",
      },
      {
        title: "Another Article",
        url: "https://example.com/another",
        description: "More chestnut content",
      },
    ];

    const formatted = formatSearchResults(results);

    expect(formatted).toContain("<search_results>");
    expect(formatted).toContain("</search_results>");
    expect(formatted).toContain('<item index="1">');
    expect(formatted).toContain('<item index="2">');
    expect(formatted).toContain("Web Page Title: Test Article");
    expect(formatted).toContain("Web Page URL: https://example.com/article");
    expect(formatted).toContain("Web Page Title: Another Article"); // 🌰
  });

  it("🌰 should handle empty results", () => {
    const formatted = formatSearchResults([]);
    expect(formatted).toContain("<search_results>");
    expect(formatted).toContain("</search_results>");
    expect(formatted).not.toContain("<item"); // 🌰
  });
});
