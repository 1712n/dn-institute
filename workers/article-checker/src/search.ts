/**
 * search.ts — Brave Search integration.
 *
 * Ports the Python BraveAPI + BraveSearchTool classes from
 * tools/article_checker/claude_retriever/searcher/searchtools/websearch.py
 *
 * Key differences from the Python version:
 *  - Uses the native fetch() API instead of requests/aiohttp (CF Workers env).
 *  - No web-page scraping / Claude summarisation step — we use description
 *    snippets from the Brave API response instead (scraping external pages
 *    inside a Worker is expensive and fragile).
 *  - Retry logic is implemented manually rather than via tenacity.
 *  - format_results_full is inlined (sourced from claude_retriever/utils.py).
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface WebSearchResult {
  url: string;
  content: string;
}

// ---------------------------------------------------------------------------
// format_results_full — port of tools/article_checker/claude_retriever/utils.py
// ---------------------------------------------------------------------------

/**
 * Wrap a list of search-result strings in the XML envelope that Claude expects.
 *
 * Python original:
 *   def format_results(extracted): ...
 *   def format_results_full(extracted): ...
 */
function formatResults(extracted: string[]): string {
  return extracted
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\n${r}\n</page_content>\n</item>`
    )
    .join("\n");
}

export function formatResultsFull(extracted: string[]): string {
  return `\n<search_results>\n${formatResults(extracted)}\n</search_results>`;
}

// ---------------------------------------------------------------------------
// BraveSearchTool
// ---------------------------------------------------------------------------

export class BraveSearchTool {
  private readonly apiKey: string;
  /** Injected into RETRIEVAL_PROMPT so Claude knows what the tool does. */
  readonly toolDescription: string;

  constructor(apiKey: string, toolDescription: string) {
    this.apiKey = apiKey;
    this.toolDescription = toolDescription;
  }

  // -------------------------------------------------------------------------
  // Low-level search with retry
  // -------------------------------------------------------------------------

  /**
   * Call the Brave Search API with simple exponential-backoff retry.
   * Mirrors the @retry decorator in BraveAPI.search().
   */
  private async rawApiSearch(
    query: string,
    maxAttempts = 10
  ): Promise<BraveApiResponse> {
    const url = new URL("https://api.search.brave.com/res/v1/web/search");
    url.searchParams.set("q", query);
    url.searchParams.set("count", "20"); // matches Python default

    let lastError: Error | undefined;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await fetch(url.toString(), {
          headers: {
            Accept: "application/json",
            "X-Subscription-Token": this.apiKey,
          },
          signal: AbortSignal.timeout(60_000),
        });

        if (!response.ok) {
          const body = await response.text();
          throw new Error(
            `Brave search HTTP ${response.status}: ${body.slice(0, 200)}`
          );
        }

        return (await response.json()) as BraveApiResponse;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));

        if (attempt < maxAttempts) {
          // Exponential backoff: 4s, 8s, 10s (capped), …
          const delay = Math.min(4_000 * Math.pow(2, attempt - 1), 10_000);
          await new Promise((r) => setTimeout(r, delay));
        }
      }
    }

    throw lastError ?? new Error("Brave search failed after all retries");
  }

  // -------------------------------------------------------------------------
  // Result parsers — ports of parse_faq / parse_news / parse_web
  // -------------------------------------------------------------------------

  private parseFaq(faq: BraveFaqItem): WebSearchResult {
    const snippet = [
      `FAQ Title: ${faq.title ?? "Unknown"}`,
      `Question: ${faq.question ?? "Unknown"}`,
      `Answer: ${faq.answer ?? "Unknown"}`,
    ].join("\n");

    return { url: faq.url ?? "", content: snippet };
  }

  private parseNews(news: BraveNewsItem): WebSearchResult | null {
    const description = news.description ?? "";
    // Throw out items where the description is tiny or doesn't exist.
    if (description.length < 5) return null;

    const snippet = [
      `News Article Title: ${news.title ?? "Unknown"}`,
      `News Article Description: ${description}`,
      `News Article Age: ${news.age ?? "Unknown"}`,
      `News Article Source: ${news.meta_url?.hostname ?? "Unknown"}`,
    ].join("\n");

    return { url: news.url ?? "", content: snippet };
  }

  private parseWeb(web: BraveWebItem): WebSearchResult {
    const url = web.url ?? "";
    // Use the description snippet from Brave (avoids scraping external sites).
    // The Python version scrapes + optionally summarises; we keep it simpler
    // for the Workers environment.
    const description = this.removeStrong(web.description ?? "");
    const snippet = [
      `Web Page Title: ${web.title ?? "Unknown"}`,
      `Web Page URL: ${url}`,
      `Web Page Description: ${description}`,
    ].join("\n");

    return { url, content: snippet };
  }

  /** Strip <strong> / </strong> tags from Brave web descriptions. */
  private removeStrong(text: string): string {
    return text
      .replace(/<strong>/g, "")
      .replace(/<\/strong>/g, "")
      .replace(/&#x27;/g, "'");
  }

  // -------------------------------------------------------------------------
  // Public search interface
  // -------------------------------------------------------------------------

  /**
   * Run a search and return up to `nResults` formatted result strings.
   * Mirrors BraveSearchTool.raw_search() + process_raw_search_results().
   */
  async search(query: string, nResults: number): Promise<string[]> {
    const response = await this.rawApiSearch(query);

    // Brave tells us the preferred ordering via response.mixed.main
    const ordering: Array<{ type: string }> =
      response.mixed?.main ?? [];

    // Pop queues for each type (mirrors the Python logic)
    const faqItems = [...(response.faq?.results ?? [])];
    const newsItems = [...(response.news?.results ?? [])];
    const webItems = [...(response.web?.results ?? [])];

    const results: WebSearchResult[] = [];

    for (const item of ordering) {
      if (results.length >= nResults) break;

      if (item.type === "web" && webItems.length > 0) {
        const parsed = this.parseWeb(webItems.shift()!);
        results.push(parsed);
      } else if (item.type === "news" && newsItems.length > 0) {
        const parsed = this.parseNews(newsItems.shift()!);
        if (parsed) results.push(parsed);
      } else if (item.type === "faq" && faqItems.length > 0) {
        const parsed = this.parseFaq(faqItems.shift()!);
        results.push(parsed);
      }
    }

    // If mixed ordering produced fewer results than requested (e.g. no mixed
    // key), fall back to whatever web items are available.
    if (results.length === 0 && webItems.length > 0) {
      for (const item of webItems.slice(0, nResults)) {
        results.push(this.parseWeb(item));
      }
    }

    return results.map((r) => r.content.trim());
  }

  /**
   * Search and return results wrapped in the <search_results> XML envelope
   * that Claude expects during the retrieval loop.
   */
  async searchFormatted(query: string, nResults: number): Promise<string> {
    const results = await this.search(query, nResults);
    return formatResultsFull(results);
  }
}

// ---------------------------------------------------------------------------
// Brave API response types (subset we actually use)
// ---------------------------------------------------------------------------

interface BraveApiResponse {
  mixed?: { main?: Array<{ type: string }> };
  faq?: { results?: BraveFaqItem[] };
  news?: { results?: BraveNewsItem[] };
  web?: { results?: BraveWebItem[] };
}

interface BraveFaqItem {
  title?: string;
  question?: string;
  answer?: string;
  url?: string;
}

interface BraveNewsItem {
  title?: string;
  description?: string;
  age?: string;
  url?: string;
  meta_url?: { hostname?: string };
}

interface BraveWebItem {
  title?: string;
  url?: string;
  description?: string;
}
