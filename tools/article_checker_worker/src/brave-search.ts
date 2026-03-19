import type { SearchResult } from './types.js'

const BRAVE_API = 'https://api.search.brave.com/res/v1/web/search'
const MAX_CONTENT_LENGTH = 1500

export async function searchWeb(
  query: string,
  apiKey: string,
  count = 5
): Promise<SearchResult[]> {
  const url = new URL(BRAVE_API)
  url.searchParams.set('q', query)
  url.searchParams.set('count', String(count))

  const res = await fetch(url.toString(), {
    headers: {
      Accept: 'application/json',
      'Accept-Encoding': 'gzip',
      'X-Subscription-Token': apiKey,
    },
  })

  if (!res.ok) {
    console.log(`Brave search failed: ${res.status}`)
    return []
  }

  const data = (await res.json()) as any
  const webResults = data?.web?.results || []

  return webResults.slice(0, count).map((r: any) => ({
    title: r.title || '',
    url: r.url || '',
    content: (r.description || '').slice(0, MAX_CONTENT_LENGTH),
  }))
}

export function formatSearchResults(results: SearchResult[]): string {
  if (results.length === 0) return '<search_results>No results found.</search_results>'

  const formatted = results
    .map(
      (r, i) =>
        `<result index="${i + 1}">\n` +
        `<title>${r.title}</title>\n` +
        `<url>${r.url}</url>\n` +
        `<content>${r.content}</content>\n` +
        `</result>`
    )
    .join('\n')

  return `<search_results>\n${formatted}\n</search_results>`
}
