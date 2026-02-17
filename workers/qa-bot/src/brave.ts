/**
 * Brave Search API client — lightweight, fetch-based.
 */

export interface BraveSearchResult {
  title: string;
  url: string;
  description: string;
}

export async function braveSearch(
  query: string,
  apiKey: string,
  count: number = 5
): Promise<BraveSearchResult[]> {
  const url = new URL("https://api.search.brave.com/res/v1/web/search");
  url.searchParams.set("q", query);
  url.searchParams.set("count", String(count));

  const res = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey,
    },
  });

  if (!res.ok) {
    console.error(`Brave search failed: ${res.status}`);
    return [];
  }

  const data: any = await res.json();
  const results: BraveSearchResult[] = (data.web?.results ?? []).map((r: any) => ({
    title: r.title ?? "",
    url: r.url ?? "",
    description: r.description ?? "",
  }));

  return results;
}

export function formatSearchResults(results: BraveSearchResult[]): string {
  return (
    "<search_results>\n" +
    results
      .map(
        (r, i) =>
          `<item index="${i + 1}">\n<page_content>\nTitle: ${r.title}\nURL: ${r.url}\nDescription: ${r.description}\n</page_content>\n</item>`
      )
      .join("\n") +
    "\n</search_results>"
  );
}
