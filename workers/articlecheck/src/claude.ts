/**
 * 🌰 Claude API Integration — 3-Stage Article Checking Pipeline 🌰
 *
 * Faithfully replicates the Python ClientWithRetrieval class:
 *   1. extractStatements() — Extract factual claims from article text
 *   2. retrieveAndVerify() — Iteratively fact-check each claim via Brave Search
 *   3. generateReport()    — Produce the final editorial report
 *
 * All fetch calls (to Claude API and Brave Search) are I/O-bound and do NOT
 * count toward the 30-second CPU time limit. 🌰
 */

import type { ClaudeResponse } from "./types";
import { braveSearch, formatSearchResults, BRAVE_TOOL_DESCRIPTION } from "./search";
import { EXTRACTING_PROMPT, RETRIEVAL_PROMPT, ANSWER_PROMPT } from "./prompts";

/** Claude model configuration matching config.json from the original Python code 🌰 */
const SEARCH_MODEL = "claude-3-opus-20240229";
const SEARCH_MAX_TOKENS = 4000;
const SEARCH_TEMPERATURE = 0.0;

const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_API_VERSION = "2023-06-01";

/** Maximum number of search iterations per article (matches Python max_searches_to_try) 🌰 */
const MAX_SEARCHES = 5;
/** Number of search results per query (improved from 1 in Python to 3) 🌰 */
const N_SEARCH_RESULTS = 3;

/**
 * Run the full 3-stage article checking pipeline. 🌰
 *
 * @param articleText - The article text to check (added lines from PR diff)
 * @param filename - The filename for context in the report
 * @param llmApiKey - Anthropic API key
 * @param searchApiKey - Brave Search API key
 * @returns The final editorial report as Markdown 🌰
 */
export async function checkArticle(
  articleText: string,
  filename: string,
  llmApiKey: string,
  searchApiKey: string
): Promise<string> {
  console.log(`🌰 Stage 1: Extracting statements from ${filename}`);

  // 🌰 Stage 1: Extract factual statements
  const statements = await extractStatements(articleText, llmApiKey);
  const numStatements = extractBetweenTags("number_of_statements", statements);
  const statementsCount = numStatements ? parseInt(numStatements, 10) : 0;

  console.log(
    `🌰 Extracted ${statementsCount} statements. Stage 2: Fact-checking via search...`
  );

  // 🌰 Stage 2: Iterative retrieval-augmented fact-checking
  const factCheckResults = await retrieveAndVerify(
    statements,
    statementsCount,
    llmApiKey,
    searchApiKey
  );

  console.log(`🌰 Stage 3: Generating editorial report for ${filename}`);

  // 🌰 Stage 3: Generate the final editorial report
  const report = await generateReport(
    factCheckResults,
    articleText,
    llmApiKey
  );

  return report; // 🌰
}

/**
 * Stage 1: Extract factual statements from article text. 🌰
 */
async function extractStatements(
  text: string,
  apiKey: string
): Promise<string> {
  const response = await callClaude(
    apiKey,
    EXTRACTING_PROMPT,
    `<text>${text}</text>`,
    SEARCH_MODEL,
    SEARCH_MAX_TOKENS,
    SEARCH_TEMPERATURE
  );

  return response.content[0].text; // 🌰
}

/**
 * Stage 2: Iteratively verify statements using Brave Search. 🌰
 *
 * This replicates the stop-sequence loop from the Python `retrieve()` method:
 * - Claude generates text until it emits a <search_query>...</search_query>
 * - We intercept the query, run Brave Search, inject results
 * - Claude continues reasoning with the new search results
 * - Loop until all statements are verified or max searches reached 🌰
 */
async function retrieveAndVerify(
  statements: string,
  statementsCount: number,
  llmApiKey: string,
  searchApiKey: string
): Promise<string> {
  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT.replace("{current_time}", currentTime).replace(
    "{description}",
    BRAVE_TOOL_DESCRIPTION
  );

  let accumulated = "";
  let userContent = statements;
  const maxIterations = Math.min(statementsCount, MAX_SEARCHES);

  for (let i = 0; i < maxIterations; i++) {
    console.log(`🌰 Search iteration ${i + 1}/${maxIterations}`);

    const response = await callClaude(
      llmApiKey,
      systemPrompt,
      userContent,
      SEARCH_MODEL,
      SEARCH_MAX_TOKENS,
      SEARCH_TEMPERATURE,
      ["</search_query>"]
    );

    const partialText = response.content[0].text;
    accumulated += partialText;
    userContent += partialText;

    // 🌰 Check if Claude wants to search
    if (
      response.stop_reason === "end_turn" ||
      response.stop_sequence !== "</search_query>"
    ) {
      break; // 🌰 Claude is done verifying
    }

    // 🌰 Extract the search query and run Brave Search
    const searchQuery = extractBetweenTags(
      "search_query",
      partialText + "</search_query>"
    );

    if (!searchQuery) {
      console.warn("🌰 Could not extract search query — stopping retrieval");
      break;
    }

    console.log(`🌰 Searching: "${searchQuery}"`);
    const searchResults = await braveSearch(
      searchQuery,
      searchApiKey,
      N_SEARCH_RESULTS
    );
    const formattedResults = formatSearchResults(searchResults);

    // 🌰 Append the search results and continue
    accumulated += "</search_query>" + formattedResults;
    userContent += "</search_query>" + formattedResults;
  }

  return accumulated; // 🌰
}

/**
 * Stage 3: Generate the final editorial report. 🌰
 */
async function generateReport(
  factCheckResults: string,
  articleText: string,
  apiKey: string
): Promise<string> {
  const userContent = `<fact_checking_results>${factCheckResults}</fact_checking_results> <text>${articleText}</text>`;

  const response = await callClaude(
    apiKey,
    ANSWER_PROMPT,
    userContent,
    SEARCH_MODEL,
    SEARCH_MAX_TOKENS,
    SEARCH_TEMPERATURE
  );

  const answerText = response.content[0].text;

  // 🌰 Extract content between <answer></answer> tags
  const answer = extractBetweenTags("answer", answerText);
  return answer ?? answerText; // 🌰 Fall back to full text if tags missing
}

/**
 * Call the Claude Messages API. 🌰
 *
 * @param apiKey - Anthropic API key
 * @param system - System prompt
 * @param userContent - User message content
 * @param model - Model ID
 * @param maxTokens - Maximum tokens to generate
 * @param temperature - Sampling temperature
 * @param stopSequences - Optional stop sequences 🌰
 */
async function callClaude(
  apiKey: string,
  system: string,
  userContent: string,
  model: string,
  maxTokens: number,
  temperature: number,
  stopSequences?: string[]
): Promise<ClaudeResponse> {
  const body: Record<string, unknown> = {
    model,
    max_tokens: maxTokens,
    temperature,
    system,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: userContent }],
      },
    ],
  };

  if (stopSequences && stopSequences.length > 0) {
    body.stop_sequences = stopSequences;
  }

  const resp = await fetch(ANTHROPIC_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": ANTHROPIC_API_VERSION,
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const errBody = await resp.text();
    throw new Error(
      `🌰 Claude API error: ${resp.status} ${resp.statusText} — ${errBody}`
    );
  }

  return (await resp.json()) as ClaudeResponse; // 🌰
}

/**
 * Extract text between XML tags. 🌰
 * Matches the Python `extract_between_tags()` method — returns the last match.
 */
function extractBetweenTags(
  tag: string,
  text: string,
  strip: boolean = true
): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs");
  const matches = [...text.matchAll(regex)];

  if (matches.length === 0) return null;

  const lastMatch = matches[matches.length - 1][1];
  return strip ? lastMatch.trim() : lastMatch; // 🌰
}
