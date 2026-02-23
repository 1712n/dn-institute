import type { SearchResult } from "./types"

const BRAVE_API = "https://api.search.brave.com/res/v1/web/search"

/**
 * Search the web using the Brave Search API.
 * Returns up to `count` results with title, URL, and description.
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  count: number = 3
): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    count: String(Math.min(count, 20))
  })

  const resp = await fetch(`${BRAVE_API}?${params}`, {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey
    }
  })

  if (!resp.ok) {
    console.error(`Brave Search error: ${resp.status}`)
    return []
  }

  const data = (await resp.json()) as {
    web?: { results?: Array<{ title: string; url: string; description: string }> }
  }

  const results = data.web?.results ?? []
  return results.slice(0, count).map((r) => ({
    title: r.title,
    url: r.url,
    description: cleanHtml(r.description)
  }))
}

/**
 * Strip HTML tags from Brave search descriptions.
 */
function cleanHtml(text: string): string {
  return text
    .replace(/<\/?strong>/g, "")
    .replace(/<[^>]*>/g, "")
    .replace(/&#x27;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
}

/**
 * Format search results into XML-tagged text for Claude.
 */
export function formatSearchResults(results: SearchResult[]): string {
  if (results.length === 0) {
    return "<search_results>No results found.</search_results>"
  }

  const items = results
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\nTitle: ${r.title}\nURL: ${r.url}\nDescription: ${r.description}\n</page_content>\n</item>`
    )
    .join("\n")

  return `<search_results>\n${items}\n</search_results>`
}
