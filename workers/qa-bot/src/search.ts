/**
 * Brave Search API client — lightweight, zero-dependency wrapper.
 */

const BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search";

export interface BraveResult {
  title: string;
  url: string;
  description: string;
}

/**
 * Search Brave and return the top N results (default 3).
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  count = 3
): Promise<BraveResult[]> {
  const params = new URLSearchParams({ q: query, count: String(count) });
  const res = await fetch(`${BRAVE_API_URL}?${params}`, {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey,
    },
  });

  if (!res.ok) {
    console.error(`Brave search error: ${res.status}`);
    return [];
  }

  const data = (await res.json()) as {
    web?: { results?: Array<{ title?: string; url?: string; description?: string }> };
  };

  return (data.web?.results ?? []).slice(0, count).map((r) => ({
    title: r.title ?? "",
    url: r.url ?? "",
    description: cleanDescription(r.description ?? ""),
  }));
}

function cleanDescription(desc: string): string {
  return desc
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'");
}
