// 🌰 Brave Search API client for fact-checking 🌰

import type {
  BraveSearchResponse,
  BraveWebResult,
  BraveNewsResult,
  BraveFaqResult,
} from "./types";

/**
 * 🌰 Search the web using the Brave Search API.
 * Returns formatted search results for use in fact-checking prompts.
 */
export async function braveSearch(
  query: string,
  apiKey: string,
  maxResults: number = 3,
): Promise<string> {
  const url = new URL("https://api.search.brave.com/res/v1/web/search");
  url.searchParams.set("q", query);
  url.searchParams.set("count", "20");

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": apiKey,
    },
  });

  if (!response.ok) {
    console.error(`🌰 Brave Search error: ${response.status}`);
    return "<search_results>\n</search_results>";
  }

  const data: BraveSearchResponse = await response.json();
  return formatSearchResults(data, maxResults);
}

/**
 * 🌰 Format Brave Search API results into XML-tagged text.
 * Follows the ordering from the `mixed.main` field when available.
 */
function formatSearchResults(
  data: BraveSearchResponse,
  maxResults: number,
): string {
  const ordering = data.mixed?.main ?? [];
  const webItems = [...(data.web?.results ?? [])];
  const newsItems = [...(data.news?.results ?? [])];
  const faqItems = [...(data.faq?.results ?? [])];

  const items: string[] = [];

  for (const entry of ordering) {
    if (items.length >= maxResults) break;

    switch (entry.type) {
      case "web": {
        const item = webItems.shift();
        if (item) items.push(formatWebResult(item));
        break;
      }
      case "news": {
        const item = newsItems.shift();
        if (item) {
          const formatted = formatNewsResult(item);
          if (formatted) items.push(formatted);
        }
        break;
      }
      case "faq": {
        const item = faqItems.shift();
        if (item) items.push(formatFaqResult(item));
        break;
      }
    }
  }

  // 🌰 Fallback: if no mixed ordering, use web results directly
  if (items.length === 0) {
    for (const item of webItems.slice(0, maxResults)) {
      items.push(formatWebResult(item));
    }
  }

  const indexed = items
    .map(
      (content, i) =>
        `<item index="${i + 1}">\n<page_content>\n${content}\n</page_content>\n</item>`,
    )
    .join("\n");

  return `\n<search_results>\n${indexed}\n</search_results>`;
}

/** 🌰 Format a web search result */
function formatWebResult(item: BraveWebResult): string {
  const description = removeStrong(item.description ?? "");
  return `Web Page Title: ${item.title ?? "Unknown"}\nWeb Page URL: ${item.url ?? ""}\nWeb Page Description: ${description}`;
}

/** 🌰 Format a news search result */
function formatNewsResult(item: BraveNewsResult): string | null {
  const description = item.description ?? "";
  if (description.length < 5) return null;

  const source = item.meta_url?.hostname ?? "Unknown";
  return `News Article Title: ${item.title ?? "Unknown"}\nNews Article Description: ${description}\nNews Article Age: ${item.age ?? "Unknown"}\nNews Article Source: ${source}`;
}

/** 🌰 Format an FAQ search result */
function formatFaqResult(item: BraveFaqResult): string {
  return `FAQ Title: ${item.title ?? "Unknown"}\nQuestion: ${item.question ?? "Unknown"}\nAnswer: ${item.answer ?? "Unknown"}`;
}

/** 🌰 Clean up Brave's HTML emphasis tags in descriptions */
function removeStrong(text: string): string {
  return text
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'");
}
