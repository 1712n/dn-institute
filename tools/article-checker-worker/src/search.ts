import type { BraveSearchResult } from "./types"

const BRAVE_DESCRIPTION = `Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic.`

interface BraveWebItem {
  title?: string
  url?: string
  description?: string
}

interface BraveNewsItem {
  title?: string
  url?: string
  description?: string
  age?: string
  meta_url?: { hostname?: string }
}

interface BraveMixedItem {
  type: string
}

interface BraveAPIResponse {
  mixed?: { main?: BraveMixedItem[] }
  web?: { results?: BraveWebItem[] }
  news?: { results?: BraveNewsItem[] }
}

/**
 * Remove <strong> HTML tags from Brave search descriptions.
 */
function removeStrong(text: string): string {
  return text
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'")
}

/**
 * Search the Brave API and return formatted results.
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  nResults: number = 3
): Promise<BraveSearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    count: "20",
  })

  const response = await fetch(
    `https://api.search.brave.com/res/v1/web/search?${params}`,
    {
      headers: {
        Accept: "application/json",
        "X-Subscription-Token": apiKey,
      },
    }
  )

  if (!response.ok) {
    console.error(`Brave search failed: ${response.status}`)
    return []
  }

  const data: BraveAPIResponse = await response.json()

  const ordering = data.mixed?.main || []
  const webItems = [...(data.web?.results || [])]
  const newsItems = [...(data.news?.results || [])]

  const results: BraveSearchResult[] = []

  for (const item of ordering) {
    if (results.length >= nResults) break

    if (item.type === "web" && webItems.length > 0) {
      const webItem = webItems.shift()!
      const url = webItem.url || ""
      const title = webItem.title || ""
      const description = removeStrong(webItem.description || "")
      results.push({
        url,
        content: `Web Page Title: ${title}\nWeb Page URL: ${url}\nWeb Page Description: ${description}`,
      })
    } else if (item.type === "news" && newsItems.length > 0) {
      const newsItem = newsItems.shift()!
      const description = newsItem.description || ""
      if (description.length < 5) continue

      results.push({
        url: newsItem.url || "",
        content: `News Article Title: ${newsItem.title || "Unknown"}\nNews Article Description: ${description}\nNews Article Age: ${newsItem.age || "Unknown"}\nNews Article Source: ${newsItem.meta_url?.hostname || "Unknown"}`,
      })
    }
  }

  return results
}

/**
 * Format search results into XML-style tags for Claude.
 */
export function formatSearchResults(results: BraveSearchResult[]): string {
  const items = results
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\n${r.content}\n</page_content>\n</item>`
    )
    .join("\n")
  return `\n<search_results>\n${items}\n</search_results>`
}

export { BRAVE_DESCRIPTION }
