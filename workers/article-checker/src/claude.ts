/**
 * Claude (Anthropic) API integration module.
 * Implements the retrieval-augmented fact-checking pipeline:
 *   1. Extract factual statements from article text
 *   2. Fact-check each statement using Brave Search
 *   3. Generate a final editorial report
 *
 * This mirrors the Python ClientWithRetrieval class.
 */

import type { AnthropicResponse, Env } from "./types";
import { EXTRACTING_PROMPT, RETRIEVAL_PROMPT, ANSWER_PROMPT } from "./prompts";
import { braveSearch, formatSearchResults, BRAVE_DESCRIPTION } from "./search";

const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_API_VERSION = "2023-06-01";

/**
 * Extract text between XML-like tags. Returns the last match.
 */
export function extractBetweenTags(
  tag: string,
  text: string,
  strip: boolean = true
): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs");
  const matches = [...text.matchAll(regex)];

  if (matches.length === 0) return null;

  const lastMatch = matches[matches.length - 1][1];
  return strip ? lastMatch.trim() : lastMatch;
}

/**
 * Call the Anthropic Messages API.
 *
 * @param apiKey - Anthropic API key
 * @param model - Model identifier (e.g., "claude-3-opus-20240229")
 * @param systemPrompt - System-level prompt
 * @param userContent - User message content
 * @param maxTokens - Maximum tokens in response
 * @param temperature - Sampling temperature
 * @param stopSequences - Optional stop sequences
 * @returns The API response
 */
async function callAnthropic(
  apiKey: string,
  model: string,
  systemPrompt: string,
  userContent: string,
  maxTokens: number,
  temperature: number,
  stopSequences?: string[]
): Promise<AnthropicResponse> {
  const body: Record<string, unknown> = {
    model,
    max_tokens: maxTokens,
    temperature,
    system: systemPrompt,
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

  const response = await fetch(ANTHROPIC_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": ANTHROPIC_API_VERSION,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Anthropic API error: ${response.status} ${response.statusText} - ${errorText}`
    );
  }

  return (await response.json()) as AnthropicResponse;
}

/**
 * Step 1: Extract factual statements from article text.
 * Uses Claude to identify key claims with dates, numbers, and entity names.
 *
 * @param text - The article text to analyze
 * @param env - Worker environment bindings
 * @returns Raw text with <statement> and <number_of_statements> tags
 */
async function extractStatements(text: string, env: Env): Promise<string> {
  const model = env.ANTHROPIC_SEARCH_MODEL;
  const maxTokens = parseInt(env.ANTHROPIC_SEARCH_MAX_TOKENS, 10);
  const temperature = parseFloat(env.ANTHROPIC_SEARCH_TEMPERATURE);

  const response = await callAnthropic(
    env.ANTHROPIC_API_KEY,
    model,
    EXTRACTING_PROMPT,
    `<text>${text}</text>`,
    maxTokens,
    temperature
  );

  return response.content[0].text;
}

/**
 * Step 2: Fact-check extracted statements using retrieval-augmented search.
 * Iteratively calls Claude with search queries, retrieves results from
 * Brave Search, and feeds them back until all statements are verified.
 *
 * @param statements - The extracted statements text
 * @param numStatements - Number of statements to verify
 * @param env - Worker environment bindings
 * @returns Raw text with fact-checking verdicts
 */
async function retrieveAndVerify(
  statements: string,
  numStatements: number,
  env: Env
): Promise<string> {
  const model = env.ANTHROPIC_SEARCH_MODEL;
  const maxTokens = parseInt(env.ANTHROPIC_SEARCH_MAX_TOKENS, 10);
  const temperature = parseFloat(env.ANTHROPIC_SEARCH_TEMPERATURE);
  const maxSearches = Math.min(numStatements, 5);

  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT.replace("{current_time}", currentTime).replace(
    "{description}",
    BRAVE_DESCRIPTION
  );

  let completions = "";
  let userContent = statements;

  for (let attempt = 0; attempt < maxSearches; attempt++) {
    const response = await callAnthropic(
      env.ANTHROPIC_API_KEY,
      model,
      systemPrompt,
      userContent,
      maxTokens,
      temperature,
      ["</search_query>"]
    );

    const partialCompletion = response.content[0].text;
    completions += partialCompletion;
    userContent += partialCompletion;

    if (
      response.stop_reason === "stop_sequence" &&
      response.stop_sequence === "</search_query>"
    ) {
      // Extract the search query from the partial completion
      const searchQuery = extractBetweenTags(
        "search_query",
        partialCompletion + "</search_query>"
      );

      if (!searchQuery) {
        console.error("Failed to extract search query from completion");
        break;
      }

      console.log(`Search attempt ${attempt + 1}: "${searchQuery}"`);

      // Execute the search
      const searchResults = await braveSearch(searchQuery, env.BRAVE_API_KEY, 1);
      const formattedResults = formatSearchResults(searchResults);

      completions += "</search_query>" + formattedResults;
      userContent += "</search_query>" + formattedResults;
    } else {
      // Model finished without requesting another search
      break;
    }
  }

  return completions;
}

/**
 * Step 3: Generate the final editorial report.
 * Takes the fact-checking results and original text, and produces
 * a comprehensive review with editor's notes, format checks, etc.
 *
 * @param searchResults - The raw fact-checking results
 * @param originalText - The original article text
 * @param env - Worker environment bindings
 * @returns The final formatted answer (content between <answer> tags)
 */
async function generateAnswer(
  searchResults: string,
  originalText: string,
  env: Env
): Promise<string> {
  const model = env.ANTHROPIC_SEARCH_MODEL;
  const temperature = parseFloat(env.ANTHROPIC_SEARCH_TEMPERATURE);

  const prompt = `<fact_checking_results>${searchResults}</fact_checking_results> <text>${originalText}</text>`;

  const response = await callAnthropic(
    env.ANTHROPIC_API_KEY,
    model,
    ANSWER_PROMPT,
    prompt,
    4000,
    temperature
  );

  const answer = extractBetweenTags("answer", response.content[0].text);
  return answer || response.content[0].text;
}

/**
 * Run the full article checking pipeline.
 * This is the main entry point that orchestrates all three steps.
 *
 * @param articleText - The article text extracted from the PR diff
 * @param env - Worker environment bindings
 * @returns The final editorial report as Markdown
 */
export async function checkArticle(
  articleText: string,
  env: Env
): Promise<string> {
  console.log("Step 1: Extracting factual statements...");
  const statements = await extractStatements(articleText, env);

  const numStatementsStr = extractBetweenTags(
    "number_of_statements",
    statements
  );
  const numStatements = numStatementsStr ? parseInt(numStatementsStr, 10) : 0;
  console.log(`Found ${numStatements} statements to verify`);

  if (numStatements === 0) {
    return "No factual statements were found to verify in the submitted article.";
  }

  console.log("Step 2: Fact-checking statements with search...");
  const searchResults = await retrieveAndVerify(statements, numStatements, env);

  console.log("Step 3: Generating editorial report...");
  const answer = await generateAnswer(searchResults, articleText, env);

  return answer;
}
