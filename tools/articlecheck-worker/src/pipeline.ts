import Anthropic from "@anthropic-ai/sdk";
import { braveSearch, formatSearchResults, BRAVE_DESCRIPTION } from "./brave";
import { EXTRACTING_PROMPT, RETRIEVAL_PROMPT, ANSWER_PROMPT } from "./prompts";

/**
 * Default config values — match Python config.json:
 *   ANTHROPIC_SEARCH_MODEL: "claude-3-opus-20240229"
 *   ANTHROPIC_SEARCH_TEMPERATURE: 0.0
 *   ANTHROPIC_SEARCH_MAX_TOKENS: 4000
 *
 * And article_checker_claude.py:
 *   n_search_results_to_use=1
 *   max_searches_to_try=5
 */
const DEFAULT_MODEL = "claude-3-opus-20240229";
const DEFAULT_MAX_TOKENS = 4000;
const TEMPERATURE = 0;
const N_SEARCH_RESULTS_TO_USE = 1;
const MAX_SEARCHES_TO_TRY = 5;

/**
 * Extract text between XML tags (last match).
 * Matches Python: extract_between_tags() in client.py and utils.py
 */
export function extractBetweenTags(
  tag: string,
  text: string
): string | null {
  const re = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs");
  const matches = [...text.matchAll(re)];
  if (matches.length === 0) return null;
  return matches[matches.length - 1]![1]!.trim();
}

export interface PipelineConfig {
  model: string;
  maxTokens: number;
}

/**
 * Phase 1: Extract factual statements from article text.
 * Matches Python: ClientWithRetrieval.extract_statements()
 */
async function extractStatements(
  text: string,
  client: Anthropic,
  config: PipelineConfig
): Promise<string> {
  const message = await client.messages.create({
    model: config.model,
    max_tokens: config.maxTokens,
    temperature: TEMPERATURE,
    system: EXTRACTING_PROMPT,
    messages: [{ role: "user", content: `<text>${text}</text>` }],
  });
  return (message.content[0] as Anthropic.TextBlock).text;
}

/**
 * Phase 2: Fact-check statements using Brave Search in a loop.
 *
 * Mirrors Python ClientWithRetrieval.retrieve() exactly:
 * - Single user message that accumulates all context (statements + partial responses + search results)
 * - Stop on </search_query>, run search, append results, continue
 * - Loop up to min(num_statements, max_searches_to_try) times
 * - n_search_results_to_use=1 per search (matching Python article_checker_claude.py line 47)
 * - {description} in system prompt filled with BRAVE_DESCRIPTION (matching Python line 165)
 */
async function factCheck(
  statements: string,
  client: Anthropic,
  braveApiKey: string,
  anthropicApiKey: string,
  config: PipelineConfig
): Promise<string> {
  const numMatch = extractBetweenTags("number_of_statements", statements);
  const numStatements = numMatch ? parseInt(numMatch, 10) : MAX_SEARCHES_TO_TRY;
  const maxSearches = Math.min(numStatements, MAX_SEARCHES_TO_TRY);

  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT
    .replace("{current_time}", currentTime)
    .replace("{description}", BRAVE_DESCRIPTION);

  let accumulated = "";
  let conversationText = statements;

  for (let i = 0; i < maxSearches; i++) {
    const message = await client.messages.create({
      model: config.model,
      max_tokens: config.maxTokens,
      temperature: TEMPERATURE,
      system: systemPrompt,
      messages: [{ role: "user", content: conversationText }],
      stop_sequences: ["</search_query>"],
    });

    const block = message.content[0] as Anthropic.TextBlock;
    const partial = block.text;
    accumulated += partial;
    conversationText += partial;

    // Match Python: if stop_reason == 'stop_sequence' and stop_seq == '</search_query>'
    if (
      message.stop_reason !== "stop_sequence"
    ) {
      break;
    }

    // Extract search query
    const query = extractBetweenTags(
      "search_query",
      partial + "</search_query>"
    );
    if (!query) break;

    // Run Brave search with n_search_results_to_use=1 and Claude Haiku summarization
    const searchResults = await braveSearch(
      query,
      braveApiKey,
      anthropicApiKey,
      N_SEARCH_RESULTS_TO_USE
    );
    const formatted = formatSearchResults(searchResults);

    accumulated += "</search_query>" + formatted;
    conversationText += "</search_query>" + formatted;
  }

  return accumulated;
}

/**
 * Phase 3: Generate editorial review from fact-check results.
 * Matches Python: ClientWithRetrieval.answer_with_results()
 */
async function editorialReview(
  factCheckResults: string,
  articleText: string,
  client: Anthropic,
  config: PipelineConfig
): Promise<string> {
  const prompt = `<fact_checking_results>${factCheckResults}</fact_checking_results> <text>${articleText}</text>`;

  const message = await client.messages.create({
    model: config.model,
    max_tokens: config.maxTokens,
    temperature: TEMPERATURE,
    system: ANSWER_PROMPT,
    messages: [{ role: "user", content: prompt }],
  });

  const text = (message.content[0] as Anthropic.TextBlock).text;
  return extractBetweenTags("answer", text) ?? text;
}

/**
 * Run the full 3-phase article check pipeline.
 *
 * Matches Python: ClientWithRetrieval.completion_with_retrieval()
 *   Phase 1: extract_statements() → extract factual claims
 *   Phase 2: retrieve() → fact-check via Brave Search + Claude loop
 *   Phase 3: answer_with_results() → comprehensive editorial review
 */
export async function runPipeline(
  articleText: string,
  anthropicApiKey: string,
  braveApiKey: string,
  model?: string,
  maxTokens?: number
): Promise<string> {
  const client = new Anthropic({ apiKey: anthropicApiKey });
  const config: PipelineConfig = {
    model: model ?? DEFAULT_MODEL,
    maxTokens: maxTokens ?? DEFAULT_MAX_TOKENS,
  };

  const statements = await extractStatements(articleText, client, config);

  const factCheckResults = await factCheck(
    statements,
    client,
    braveApiKey,
    anthropicApiKey,
    config
  );

  const review = await editorialReview(
    factCheckResults,
    articleText,
    client,
    config
  );

  return review;
}
