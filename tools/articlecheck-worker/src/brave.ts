import Anthropic from "@anthropic-ai/sdk";

/**
 * Brave Search Tool description — injected into RETRIEVAL_PROMPT's {description} placeholder.
 * Preserved verbatim from Python: claude_retriever/searcher/searchtools/websearch.py
 */
export const BRAVE_DESCRIPTION =
  "Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic.";

/**
 * Summarization model config — matches Python config.json:
 *   ANTHROPIC_SUMMARIZE_MODEL: "claude-3-haiku-20240307"
 *   ANTHROPIC_SUMMARIZE_TEMPERATURE: 0.0
 *   ANTHROPIC_SUMMARIZE_MAX_TOKENS: 512
 */
const SUMMARIZE_MODEL = "claude-3-haiku-20240307";
const SUMMARIZE_MAX_TOKENS = 512;
const SUMMARIZE_TEMPERATURE = 0;

// ─── Retry ──────────────────────────────────────────────────────────────────

/**
 * Retry with exponential backoff. Matches Python tenacity config:
 *   @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(10))
 */
async function withRetry<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 10,
  minDelayMs: number = 4000,
  maxDelayMs: number = 10000
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < maxAttempts - 1) {
        const delay = Math.min(
          minDelayMs * Math.pow(2, attempt),
          maxDelayMs
        );
        await new Promise((r) => setTimeout(r, delay));
      }
    }
  }
  throw lastError;
}

// ─── HTMLRewriter-based Text Extraction ─────────────────────────────────────

/**
 * Extract visible text from an HTML Response using Cloudflare's HTMLRewriter.
 *
 * This is the Workers-native equivalent of BeautifulSoup's get_text(strip=True, separator='\n').
 * HTMLRewriter is a streaming parser — far more efficient than loading the entire DOM,
 * and unlike regex, it correctly handles nested tags, CDATA, comments, etc.
 */
async function extractTextFromHtml(response: Response): Promise<string> {
  let collected = "";

  // Strip script/style/noscript and collect visible text.
  // Only these three are stripped — matching Python BeautifulSoup get_text() behavior
  // which extracts ALL visible text (including nav/header/footer).
  // Claude Haiku handles further content filtering in the summarization step.
  const rewriter = new HTMLRewriter()
    .on("script", { element(el) { el.remove(); } })
    .on("style", { element(el) { el.remove(); } })
    .on("noscript", { element(el) { el.remove(); } })
    .on("*", {
      text(chunk) {
        collected += chunk.text;
        if (chunk.lastInTextNode) {
          collected += "\n";
        }
      },
    });

  // Must consume the transformed response to trigger all handlers
  await rewriter.transform(response).text();

  // Collapse whitespace (mirrors bleach.clean + BeautifulSoup get_text(strip=True))
  return collected
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .join("\n");
}

/**
 * Fetch a web page and extract text content using HTMLRewriter.
 * Matches Python: get_url_content() with BeautifulSoup + bleach
 */
async function fetchPageContent(
  url: string,
  timeoutMs: number = 10000
): Promise<string | null> {
  try {
    if (!isValidUrl(url)) return null;

    const resp = await fetch(url, {
      headers: { "User-Agent": "Mozilla/5.0" },
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (!resp.ok) return null;

    const text = await extractTextFromHtml(resp);
    return text.length > 50 ? text : null;
  } catch {
    return null;
  }
}

function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

// ─── Claude Haiku Summarization ─────────────────────────────────────────────

/**
 * Summarize scraped page content using Claude Haiku.
 * Matches Python: claude_extract_article() in utils.py
 *
 * Sends raw page content to Claude Haiku for focused article extraction,
 * stripping nav, ads, sidebars, footers. This is the key quality step.
 */
async function summarizeWithClaude(
  content: string,
  query: string,
  anthropicApiKey: string,
  maxTokensToRead: number = 20_000
): Promise<string> {
  // Truncate if too long (matches Python tokenizer truncation)
  // ~4 chars per token for English text
  const maxChars = maxTokensToRead * 4;
  if (content.length > maxChars) {
    content = content.slice(0, maxChars);
  }

  const promptText =
    `Here is the content from a web page. Please extract only the article from this content:\n${content}` +
    `\nThis extraction is in response to the following user query:\n${query}`;

  const instructions = `
    Extract the main article content from this web page, excluding site navigation, advertisements, sidebars, and other non-essential elements. Ensure the extracted text is clean and contains only the relevant information focusing solely on the primary article.
    `;

  const client = new Anthropic({ apiKey: anthropicApiKey });
  const response = await client.messages.create({
    model: SUMMARIZE_MODEL,
    stop_sequences: ["</article>"],
    max_tokens: SUMMARIZE_MAX_TOKENS,
    temperature: SUMMARIZE_TEMPERATURE,
    messages: [{ role: "user", content: `${promptText} ${instructions}` }],
  });

  let extracted = (response.content[0] as Anthropic.TextBlock).text;
  if (!extracted.endsWith("</article>")) {
    extracted += "</article>";
  }
  return `<article>${extracted}`;
}

/**
 * Scrape a URL and summarize with Claude.
 * Matches Python: scrape_url(url, summarize_with_claude=True, ...)
 */
async function scrapeUrl(
  url: string,
  query: string,
  anthropicApiKey: string
): Promise<string> {
  const content = await fetchPageContent(url);
  if (!content) return "CONTENT NOT AVAILABLE";

  try {
    return await summarizeWithClaude(content, query, anthropicApiKey);
  } catch {
    // Fall back to raw content on summarization failure
    // Matches Python: "Failed to extract with Claude. Falling back to raw content."
    return content;
  }
}

// ─── Brave Search API ───────────────────────────────────────────────────────

interface BraveSearchResponse {
  web?: { results?: Array<{ title: string; url: string; description: string }> };
  news?: {
    results?: Array<{
      title: string;
      url: string;
      description: string;
      age?: string;
      meta_url?: { hostname?: string };
    }>;
  };
  faq?: {
    results?: Array<{
      title: string;
      url: string;
      question: string;
      answer: string;
    }>;
  };
  mixed?: { main?: Array<{ type: string }> };
}

function removeStrong(text: string): string {
  return text
    .replace(/<strong>/g, "")
    .replace(/<\/strong>/g, "")
    .replace(/&#x27;/g, "'");
}

/**
 * Search Brave and return formatted results with page scraping + Claude summarization.
 *
 * Matches Python BraveSearchTool.raw_search() exactly:
 * 1. Call Brave API (with retry)
 * 2. Use `mixed.main` ordering to interleave web/news/faq in correct rank order
 * 3. For web results: scrape page content via HTMLRewriter + summarize with Claude Haiku
 * 4. For news results: include title, description, age, source
 * 5. For FAQ results: include title, question, answer
 * 6. Return n_search_results_to_use results
 */
export async function braveSearch(
  query: string,
  braveApiKey: string,
  anthropicApiKey: string,
  nSearchResultsToUse: number = 1
): Promise<string[]> {
  return withRetry(() =>
    braveSearchInner(query, braveApiKey, anthropicApiKey, nSearchResultsToUse)
  );
}

async function braveSearchInner(
  query: string,
  braveApiKey: string,
  anthropicApiKey: string,
  nSearchResultsToUse: number
): Promise<string[]> {
  const params = new URLSearchParams({ q: query, count: "20" });
  const resp = await fetch(
    `https://api.search.brave.com/res/v1/web/search?${params}`,
    {
      headers: {
        Accept: "application/json",
        "X-Subscription-Token": braveApiKey,
      },
    }
  );

  if (!resp.ok) return [];
  const data = (await resp.json()) as BraveSearchResponse;

  // Use Brave's mixed ordering for correct ranking
  // Matches Python: correct_ordering = search_response.get("mixed", {}).get("main", [])
  const ordering = data.mixed?.main ?? [];
  const webItems = [...(data.web?.results ?? [])];
  const newsItems = [...(data.news?.results ?? [])];
  const faqItems = [...(data.faq?.results ?? [])];

  const results: string[] = [];
  const webScrapeTasks: Array<{
    index: number;
    url: string;
    title: string;
    desc: string;
  }> = [];

  // First pass: collect items in ranked order, queue web scraping
  for (const item of ordering) {
    if (results.length >= nSearchResultsToUse) break;

    if (item.type === "web" && webItems.length > 0) {
      const web = webItems.shift()!;
      const desc = removeStrong(web.description ?? "");
      // Placeholder — replaced with scraped content below
      results.push(
        `Web Page Title: ${web.title}\nWeb Page URL: ${web.url}\nWeb Page Description: ${desc}`
      );
      webScrapeTasks.push({
        index: results.length - 1,
        url: web.url,
        title: web.title,
        desc,
      });
    } else if (item.type === "news" && newsItems.length > 0) {
      const news = newsItems.shift()!;
      if (news.description && news.description.length > 5) {
        results.push(
          `News Article Title: ${news.title}\n` +
            `News Article Description: ${news.description}\n` +
            `News Article Age: ${news.age ?? "Unknown"}\n` +
            `News Article Source: ${news.meta_url?.hostname ?? "Unknown"}`
        );
      }
    } else if (item.type === "faq" && faqItems.length > 0) {
      const faq = faqItems.shift()!;
      results.push(
        `FAQ Title: ${faq.title ?? "Unknown"}\n` +
          `Question: ${faq.question ?? "Unknown"}\n` +
          `Answer: ${faq.answer ?? "Unknown"}`
      );
    }
  }

  // Fallback if mixed ordering is empty/missing
  if (results.length === 0) {
    for (const web of webItems.slice(0, nSearchResultsToUse)) {
      const desc = removeStrong(web.description ?? "");
      results.push(
        `Web Page Title: ${web.title}\nWeb Page URL: ${web.url}\nWeb Page Description: ${desc}`
      );
      webScrapeTasks.push({
        index: results.length - 1,
        url: web.url,
        title: web.title,
        desc,
      });
    }
  }

  // Scrape web pages in parallel + summarize with Claude Haiku
  // Matches Python: asyncio.gather(*web_parsing_tasks)
  if (webScrapeTasks.length > 0) {
    const scraped = await Promise.allSettled(
      webScrapeTasks.map((task) =>
        scrapeUrl(task.url, query, anthropicApiKey)
      )
    );

    for (let i = 0; i < webScrapeTasks.length; i++) {
      const task = webScrapeTasks[i]!;
      const result = scraped[i]!;

      let snippet = `Web Page Title: ${task.title}\nWeb Page URL: ${task.url}`;
      if (result.status === "fulfilled" && result.value !== "CONTENT NOT AVAILABLE") {
        const content = result.value;
        if (content.startsWith("<summary>") || content.startsWith("<article>")) {
          snippet += `\nWeb Page Summary: ${content}`;
        } else {
          snippet += `\nWeb Page Content: ${content}`;
        }
      } else {
        snippet += `\nWeb Page Description: ${task.desc}`;
      }
      results[task.index] = snippet;
    }
  }

  return results.slice(0, nSearchResultsToUse);
}

// ─── Formatting ─────────────────────────────────────────────────────────────

/**
 * Format search results into XML string for Claude.
 * Matches Python: format_results_full() in utils.py
 */
export function formatSearchResults(results: string[]): string {
  const items = results
    .map(
      (r, i) =>
        `<item index="${i + 1}">\n<page_content>\n${r}\n</page_content>\n</item>`
    )
    .join("\n");
  return `\n<search_results>\n${items}\n</search_results>`;
}
