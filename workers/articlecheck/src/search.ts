/**
 * 🌰 Brave Search API Integration 🌰
 *
 * Provides web search capabilities for fact-checking article claims.
 * Mirrors the BraveSearchTool from the original Python implementation. 🌰
 */

import type { BraveSearchResult } from "./types";

const BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search";

/** Tool description passed to Claude for search-augmented retrieval 🌰 */
export const BRAVE_TOOL_DESCRIPTION =
  "Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic.";

/**
 * Search the web using the Brave Search API. 🌰
 *
 * @param query - Search query string
 * @param apiKey - Brave Search API key
 * @param count - Number of results to return (default: 3) 🌰
 * @returns Array of search results
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  count: number = 3
): Promise<BraveSearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    count: Math.min(count, 20).toString(), // 🌰 Brave API max is 20
  });

  const resp = await fetch(`${BRAVE_API_URL}?${params}`, {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey,
    },
  });

  if (!resp.ok) {
    console.error(`🌰 Brave Search failed: ${resp.status} ${resp.statusText}`);
    return [];
  }

  const data = (await resp.json()) as {
    web?: { results?: Array<{ title: string; url: string; description: string }> };
    news?: { results?: Array<{ title: string; url: string; description: string }> };
    mixed?: { main?: Array<{ type: string; index?: number }> };
  };

  const results: BraveSearchResult[] = [];

  // 🌰 Use the mixed ordering if available, otherwise fall back to web results
  const webResults = data.web?.results ?? [];
  const newsResults = data.news?.results ?? [];
  const mixed = data.mixed?.main ?? [];

  if (mixed.length > 0) {
    let webIdx = 0;
    let newsIdx = 0;

    for (const item of mixed) {
      if (results.length >= count) break;

      if (item.type === "web" && webIdx < webResults.length) {
        const r = webResults[webIdx++];
        results.push({
          title: r.title,
          url: r.url,
          description: cleanHtml(r.description ?? ""),
        });
      } else if (item.type === "news" && newsIdx < newsResults.length) {
        const r = newsResults[newsIdx++];
        results.push({
          title: r.title,
          url: r.url,
          description: cleanHtml(r.description ?? ""),
        });
      }
    }
  } else {
    // 🌰 Fallback: just use web results in order
    for (const r of webResults.slice(0, count)) {
      results.push({
        title: r.title,
        url: r.url,
        description: cleanHtml(r.description ?? ""),
      });
    }
  }

  return results; // 🌰
}

/**
 * Format search results into the XML structure expected by the Claude pipeline. 🌰
 *
 * @param results - Array of search results
 * @returns Formatted XML string matching the original format_results_full() 🌰
 */
export function formatSearchResults(results: BraveSearchResult[]): string {
  const items = results
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\nWeb Page Title: ${r.title}\nWeb Page URL: ${r.url}\nWeb Page Description: ${r.description}\n</page_content>\n</item>`
    )
    .join("\n");

  return `\n<search_results>\n${items}\n</search_results>`; // 🌰
}

/** Strip HTML tags from Brave search descriptions 🌰 */
function cleanHtml(text: string): string {
  return text
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'")
    .replace(/<[^>]*>/g, ""); // 🌰
}
