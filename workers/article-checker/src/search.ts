/**
 * Brave Search API integration module.
 * Mirrors the Python BraveSearchTool functionality.
 */

import type { SearchResult, Env } from "./types";

const BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search";

export const BRAVE_DESCRIPTION = `Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic.`;

/**
 * A search result item from Brave API.
 */
interface BraveWebResult {
  title: string;
  url: string;
  description: string;
}

interface BraveNewsResult {
  title: string;
  url: string;
  description: string;
  age?: string;
  meta_url?: { hostname?: string };
}

interface BraveFaqResult {
  title: string;
  url: string;
  question: string;
  answer: string;
}

interface BraveMixedItem {
  type: string;
}

interface BraveSearchResponse {
  mixed?: { main?: BraveMixedItem[] };
  web?: { results?: BraveWebResult[] };
  news?: { results?: BraveNewsResult[] };
  faq?: { results?: BraveFaqResult[] };
}

/**
 * Remove HTML <strong> tags and entity references from text.
 */
function cleanDescription(text: string): string {
  return text
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'");
}

/**
 * Parse a FAQ result into a SearchResult.
 */
function parseFaq(faq: BraveFaqResult): SearchResult {
  const snippet = `FAQ Title: ${faq.title || "Unknown"}
Question: ${faq.question || "Unknown"}
Answer: ${faq.answer || "Unknown"}`;

  return { url: faq.url || "", content: snippet };
}

/**
 * Parse a news result into a SearchResult.
 */
function parseNews(news: BraveNewsResult): SearchResult | null {
  const description = news.description || "";
  if (description.length < 5) return null;

  const snippet = `News Article Title: ${news.title || "Unknown"}
News Article Description: ${description}
News Article Age: ${news.age || "Unknown"}
News Article Source: ${news.meta_url?.hostname || "Unknown"}`;

  return { url: news.url || "", content: snippet };
}

/**
 * Parse a web result into a SearchResult.
 * Unlike the Python version, we do not scrape full page content since
 * Cloudflare Workers have limited execution time. We use the Brave
 * description snippet which is more resource-efficient.
 */
function parseWeb(web: BraveWebResult): SearchResult {
  const snippet = `Web Page Title: ${web.title || "Unknown"}
Web Page URL: ${web.url || ""}
Web Page Description: ${cleanDescription(web.description || "")}`;

  return { url: web.url || "", content: snippet };
}

/**
 * Execute a search query against the Brave Search API.
 *
 * @param query - The search query
 * @param apiKey - Brave Search API key
 * @param nResults - Maximum number of results to return
 * @returns Array of search results
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  nResults: number = 3
): Promise<SearchResult[]> {
  const url = new URL(BRAVE_SEARCH_URL);
  url.searchParams.set("q", query);
  url.searchParams.set("count", "20");

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey,
    },
  });

  if (!response.ok) {
    console.error(`Brave search failed: ${response.status} ${await response.text()}`);
    return [];
  }

  const data = (await response.json()) as BraveSearchResponse;

  // Get the correct ordering from the mixed results
  const ordering = data.mixed?.main || [];
  const webItems = [...(data.web?.results || [])];
  const newsItems = [...(data.news?.results || [])];
  const faqItems = [...(data.faq?.results || [])];

  const results: SearchResult[] = [];

  for (const item of ordering) {
    if (results.length >= nResults) break;

    if (item.type === "web" && webItems.length > 0) {
      const webItem = webItems.shift()!;
      results.push(parseWeb(webItem));
    } else if (item.type === "news" && newsItems.length > 0) {
      const newsItem = newsItems.shift()!;
      const parsed = parseNews(newsItem);
      if (parsed) results.push(parsed);
    } else if (item.type === "faq" && faqItems.length > 0) {
      const faqItem = faqItems.shift()!;
      results.push(parseFaq(faqItem));
    }
  }

  return results;
}

/**
 * Format search results into XML-like tags for Claude.
 * Mirrors the Python format_results_full() function.
 *
 * @param results - The search results to format
 * @returns Formatted string with <search_results> tags
 */
export function formatSearchResults(results: SearchResult[]): string {
  const items = results
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\n${r.content}\n</page_content>\n</item>`
    )
    .join("\n");

  return `\n<search_results>\n${items}\n</search_results>`;
}
