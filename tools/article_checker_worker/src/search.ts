/**
 * 🌰 Brave Search API client — web search for fact-checking pipeline
 */

import type { BraveSearchResponse, SearchResult } from "./types"

const BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

/**
 * Brave Search tool description passed to Claude for agentic search.
 */
export const BRAVE_DESCRIPTION =
  "Brave Search Engine Tool: The search engine will search using the Brave search engine " +
  "for web pages with keywords similar to your query. It returns for each page its title, " +
  "a summary and potentially the full page content. Use this tool if you want to get " +
  "up-to-date and comprehensive information on a topic."

/**
 * Search Brave and return structured results.
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  count: number = 5
): Promise<SearchResult[]> {
  const url = new URL(BRAVE_SEARCH_URL)
  url.searchParams.set("q", query)
  url.searchParams.set("count", String(Math.min(count, 20)))

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey,
    },
  })

  if (!response.ok) {
    console.error(`Brave search failed: ${response.status}`)
    return []
  }

  const data: BraveSearchResponse = await response.json()
  return parseSearchResponse(data, count)
}

/**
 * Parse Brave API response into ordered search results.
 * Follows the mixed.main ordering like the Python implementation.
 */
function parseSearchResponse(
  data: BraveSearchResponse,
  maxResults: number
): SearchResult[] {
  const results: SearchResult[] = []
  const ordering = data.mixed?.main ?? []

  const webItems = [...(data.web?.results ?? [])]
  const newsItems = [...(data.news?.results ?? [])]
  const faqItems = [...(data.faq?.results ?? [])]

  for (const item of ordering) {
    if (results.length >= maxResults) break

    if (item.type === "web" && webItems.length > 0) {
      const web = webItems.shift()!
      const description = cleanHtml(web.description ?? "")
      results.push({
        url: web.url,
        content: `Web Page Title: ${web.title}\nWeb Page URL: ${web.url}\nWeb Page Description: ${description}`,
      })
    } else if (item.type === "news" && newsItems.length > 0) {
      const news = newsItems.shift()!
      if ((news.description?.length ?? 0) < 5) continue
      results.push({
        url: news.url,
        content:
          `News Article Title: ${news.title}\n` +
          `News Article Description: ${news.description}\n` +
          `News Article Age: ${news.age ?? "Unknown"}\n` +
          `News Article Source: ${news.meta_url?.hostname ?? "Unknown"}`,
      })
    } else if (item.type === "faq" && faqItems.length > 0) {
      const faq = faqItems.shift()!
      results.push({
        url: faq.url,
        content:
          `FAQ Title: ${faq.title}\n` +
          `Question: ${faq.question}\n` +
          `Answer: ${faq.answer}`,
      })
    }
  }

  // If mixed ordering is empty, fall back to web results
  if (results.length === 0) {
    for (const web of webItems.slice(0, maxResults)) {
      results.push({
        url: web.url,
        content: `Web Page Title: ${web.title}\nWeb Page URL: ${web.url}\nWeb Page Description: ${cleanHtml(web.description ?? "")}`,
      })
    }
  }

  return results
}

/**
 * Remove HTML tags from Brave search descriptions.
 */
function cleanHtml(text: string): string {
  return text
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'")
    .replace(/<[^>]*>/g, "")
}

/**
 * Format search results into XML structure matching the Python implementation.
 */
export function formatSearchResults(results: SearchResult[]): string {
  const items = results
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\n${r.content}\n</page_content>\n</item>`
    )
    .join("\n")
  return `\n<search_results>\n${items}\n</search_results>`
}
