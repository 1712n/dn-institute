import { callClaude } from "./claude";
import { EXTRACTING_PROMPT, RETRIEVAL_PROMPT, ANSWER_PROMPT } from "./prompts";
import type { BraveSearchResponse, BraveSearchResult, DiffFile } from "./types";

/**
 * Run the full article analysis pipeline:
 *   1. Extract factual statements from the article text
 *   2. Verify statements via search + Claude (retrieval loop)
 *   3. Produce a final editorial review
 *
 * Ported from tools/article_checker/claude_retriever/client.py
 */
export async function analyzeArticle(
  diffFiles: DiffFile[],
  apiKey: string,
  braveApiKey: string,
  model: string,
  maxTokens: number
): Promise<string> {
  if (diffFiles.length === 0) {
    return "⚠️ No file changes detected in this PR.";
  }

  // Combine all additions with filenames (same as Python: diff[0]['header'] + diff[0]['body'][0]['body'])
  const articleText = diffFiles
    .map((f) => `**File: ${f.filename}**\n${f.additions}`)
    .join("\n\n");

  // Step 1: Extract factual statements
  const extractedStatements = await callClaude(
    EXTRACTING_PROMPT,
    `<text>${articleText}</text>`,
    apiKey,
    model,
    maxTokens,
    0.0
  );

  // Step 2: Retrieval-augmented fact-checking loop
  const numMatch = extractedStatements.text.match(
    /<number_of_statements>\s*(\d+)\s*<\/number_of_statements>/
  );
  const numStatements = numMatch ? parseInt(numMatch[1], 10) : 5;
  const maxSearches = Math.min(numStatements, 5);

  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT.replace("{current_time}", currentTime);

  let accumulatedText = extractedStatements.text;
  let completions = "";

  for (let i = 0; i < maxSearches; i++) {
    const result = await callClaude(
      systemPrompt,
      accumulatedText,
      apiKey,
      model,
      maxTokens,
      0.0,
      ["</search_query>"]
    );

    completions += result.text;
    accumulatedText += result.text;

    if (
      result.stopReason === "stop_sequence" ||
      result.stopSequence === "</search_query>"
    ) {
      // Extract the search query from the partial completion
      const queryMatch = result.text.match(
        /<search_query>([\s\S]*?)$/
      );
      const searchQuery = queryMatch ? queryMatch[1].trim() : "";

      if (searchQuery) {
        const searchResults = await braveSearch(searchQuery, braveApiKey);
        const formattedResults = formatSearchResults(searchResults);
        const fragment = `</search_query>${formattedResults}`;
        completions += fragment;
        accumulatedText += fragment;
      }
    } else {
      // Claude stopped naturally — done with fact-checking
      break;
    }
  }

  // Step 3: Final editorial answer
  const factCheckResults = completions;
  const answerPromptText = `<fact_checking_results>${factCheckResults}</fact_checking_results> <text>${articleText}</text>`;

  const finalResult = await callClaude(
    ANSWER_PROMPT,
    answerPromptText,
    apiKey,
    model,
    maxTokens,
    0.0
  );

  // Extract content between <answer> tags if present
  const answerMatch = finalResult.text.match(
    /<answer>([\s\S]*?)<\/answer>/
  );

  return answerMatch ? answerMatch[1].trim() : finalResult.text;
}

/**
 * Search the web using Brave Search API.
 */
async function braveSearch(
  query: string,
  apiKey: string,
  count: number = 3
): Promise<BraveSearchResult[]> {
  const url = new URL("https://api.search.brave.com/res/v1/web/search");
  url.searchParams.set("q", query);
  url.searchParams.set("count", String(count));

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      "Accept-Encoding": "gzip",
      "X-Subscription-Token": apiKey,
    },
  });

  if (!response.ok) {
    console.error(`Brave Search failed: HTTP ${response.status}`);
    return [];
  }

  const data = (await response.json()) as BraveSearchResponse;
  return data.web?.results ?? [];
}

/**
 * Format search results as XML — same format as the Python version's
 * format_results_full() for the Claude retrieval prompt.
 */
function formatSearchResults(results: BraveSearchResult[]): string {
  let xml = "\n<search_results>\n";
  results.forEach((r, i) => {
    xml += `<item index="${i + 1}">\n`;
    xml += `<page_content>\n`;
    xml += `Web Page Title: ${r.title}\n`;
    xml += `Web Page URL: ${r.url}\n`;
    xml += `Web Page Summary: <summary>${stripHtml(r.description)}</summary>\n`;
    xml += `</page_content>\n`;
    xml += `</item>\n`;
  });
  xml += "</search_results>\n";
  return xml;
}

/** Strip HTML tags from a string */
function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, "");
}
