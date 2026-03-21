import { describe, it, expect } from "vitest";
import { formatSearchResults, BRAVE_DESCRIPTION } from "../src/brave";

describe("BRAVE_DESCRIPTION", () => {
  it("matches the Python BRAVE_DESCRIPTION exactly", () => {
    expect(BRAVE_DESCRIPTION).toBe(
      "Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic."
    );
  });
});

describe("formatSearchResults", () => {
  it("formats results into XML search_results", () => {
    const results = ["Result 1 content", "Result 2 content"];
    const formatted = formatSearchResults(results);

    expect(formatted).toContain("<search_results>");
    expect(formatted).toContain("</search_results>");
    expect(formatted).toContain('<item index="1">');
    expect(formatted).toContain('<item index="2">');
    expect(formatted).toContain("<page_content>");
    expect(formatted).toContain("Result 1 content");
    expect(formatted).toContain("Result 2 content");
  });

  it("handles empty results", () => {
    const formatted = formatSearchResults([]);
    expect(formatted).toContain("<search_results>");
    expect(formatted).toContain("</search_results>");
    expect(formatted).not.toContain("<item");
  });

  it("handles results with special characters", () => {
    const results = ['Content with <html> tags & "quotes" and \'apostrophes\''];
    const formatted = formatSearchResults(results);
    expect(formatted).toContain("<html>");
    expect(formatted).toContain("&");
  });

  it("indexes start at 1, not 0", () => {
    const formatted = formatSearchResults(["a", "b", "c"]);
    expect(formatted).toContain('index="1"');
    expect(formatted).toContain('index="2"');
    expect(formatted).toContain('index="3"');
    expect(formatted).not.toContain('index="0"');
  });

  it("matches Python format_results_full output structure", () => {
    // Python: f'\n<search_results>\n{format_results(extracted)}\n</search_results>'
    // Python format_results: f'<item index="{i+1}">\n<page_content>\n{r}\n</page_content>\n</item>'
    const formatted = formatSearchResults(["test"]);
    expect(formatted).toBe(
      '\n<search_results>\n<item index="1">\n<page_content>\ntest\n</page_content>\n</item>\n</search_results>'
    );
  });
});
