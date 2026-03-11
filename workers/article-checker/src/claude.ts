// 🌰 Claude API client for fact-checking and review generation 🌰

import type { ClaudeResponse } from "./types";
import {
  EXTRACTING_PROMPT,
  buildRetrievalPrompt,
  ANSWER_PROMPT,
  BRAVE_TOOL_DESCRIPTION,
} from "./prompts";
import { braveSearch } from "./search";

const CLAUDE_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";

// 🌰 Model configuration matching the original bot's config.json
const SEARCH_MODEL = "claude-3-opus-20240229";
const SEARCH_MAX_TOKENS = 4000;
const SEARCH_TEMPERATURE = 0;

/**
 * 🌰 Run the full article checking pipeline:
 * 1. Extract factual statements from article text
 * 2. Verify each statement via Brave Search
 * 3. Generate a comprehensive review comment
 */
export async function runArticleCheck(
  articleText: string,
  anthropicApiKey: string,
  braveApiKey: string,
): Promise<string> {
  console.log("🌰 Step 1: Extracting factual statements...");
  const statements = await extractStatements(articleText, anthropicApiKey);

  console.log("🌰 Step 2: Verifying statements via search...");
  const searchResults = await verifyStatements(
    statements,
    anthropicApiKey,
    braveApiKey,
  );

  console.log("🌰 Step 3: Generating review comment...");
  const answer = await generateReview(
    searchResults,
    articleText,
    anthropicApiKey,
  );

  return answer;
}

/**
 * 🌰 Extract factual statements from article text using Claude.
 */
async function extractStatements(
  text: string,
  apiKey: string,
): Promise<string> {
  const response = await callClaude({
    apiKey,
    model: SEARCH_MODEL,
    maxTokens: SEARCH_MAX_TOKENS,
    temperature: SEARCH_TEMPERATURE,
    system: EXTRACTING_PROMPT,
    userMessage: `<text>${text}</text>`,
  });

  return response.content[0].text;
}

/**
 * 🌰 Verify extracted statements by iteratively searching and checking.
 * Implements the search-loop pattern from the original Python bot.
 */
async function verifyStatements(
  statements: string,
  apiKey: string,
  braveApiKey: string,
): Promise<string> {
  // 🌰 Parse the number of statements to determine max search iterations
  const numMatch = statements.match(
    /<number_of_statements>\s*(\d+)\s*<\/number_of_statements>/,
  );
  const numStatements = numMatch ? parseInt(numMatch[1], 10) : 5;
  const maxSearches = Math.min(numStatements, 5);

  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = buildRetrievalPrompt(currentTime, BRAVE_TOOL_DESCRIPTION);

  let completions = "";
  let userContent = statements;

  for (let attempt = 0; attempt < maxSearches; attempt++) {
    const response = await callClaude({
      apiKey,
      model: SEARCH_MODEL,
      maxTokens: SEARCH_MAX_TOKENS,
      temperature: SEARCH_TEMPERATURE,
      system: systemPrompt,
      userMessage: userContent,
      stopSequences: ["</search_query>"],
    });

    const partialText = response.content[0].text;
    completions += partialText;
    userContent += partialText;

    // 🌰 If Claude issued a search query, run it and feed results back
    if (
      response.stop_reason === "end_turn" ||
      response.stop_sequence !== "</search_query>"
    ) {
      break;
    }

    const query = extractBetweenTags(
      "search_query",
      partialText + "</search_query>",
    );
    if (!query) break;

    console.log(`🌰 Search attempt ${attempt + 1}: "${query}"`);
    const searchResults = await braveSearch(query, braveApiKey, 3);

    completions += "</search_query>" + searchResults;
    userContent += "</search_query>" + searchResults;
  }

  return completions;
}

/**
 * 🌰 Generate the final review comment from fact-checking results.
 */
async function generateReview(
  searchResults: string,
  articleText: string,
  apiKey: string,
): Promise<string> {
  const prompt = `<fact_checking_results>${searchResults}</fact_checking_results> <text>${articleText}</text>`;

  const response = await callClaude({
    apiKey,
    model: SEARCH_MODEL,
    maxTokens: SEARCH_MAX_TOKENS,
    temperature: SEARCH_TEMPERATURE,
    system: ANSWER_PROMPT,
    userMessage: prompt,
  });

  const text = response.content[0].text;
  const answer = extractBetweenTags("answer", text);
  return answer ?? text;
}

/**
 * 🌰 Low-level Claude Messages API call using native fetch.
 */
async function callClaude(params: {
  apiKey: string;
  model: string;
  maxTokens: number;
  temperature: number;
  system: string;
  userMessage: string;
  stopSequences?: string[];
}): Promise<ClaudeResponse> {
  const body: Record<string, unknown> = {
    model: params.model,
    max_tokens: params.maxTokens,
    temperature: params.temperature,
    system: params.system,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: params.userMessage }],
      },
    ],
  };

  if (params.stopSequences?.length) {
    body.stop_sequences = params.stopSequences;
  }

  const response = await fetch(CLAUDE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": params.apiKey,
      "anthropic-version": ANTHROPIC_VERSION,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`🌰 Claude API error ${response.status}: ${errorText}`);
  }

  return response.json();
}

/**
 * 🌰 Extract text between XML-style tags (last match).
 * Mirrors the Python extract_between_tags helper.
 */
function extractBetweenTags(tag: string, text: string): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs");
  const matches = [...text.matchAll(regex)];
  if (matches.length === 0) return null;
  return matches[matches.length - 1][1].trim();
}
