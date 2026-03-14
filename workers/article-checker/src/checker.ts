/**
 * checker.ts — Main fact-checking pipeline.
 *
 * Ports the ClientWithRetrieval class from
 * tools/article_checker/claude_retriever/client.py into three clean functions:
 *
 *   extractStatements()  — extract factual claims from article text
 *   retrieve()           — iterative Brave Search + Claude verification loop
 *   answerWithResults()  — generate the final editor's report
 *   fullCheck()          — orchestrates all three steps
 *
 * Key implementation detail (from the Python original):
 *   The retrieval loop uses stop_sequences=["</search_query>"] so that Claude
 *   signals "I want to search now" by emitting <search_query>…</search_query>.
 *   When we see stop_reason === "stop_sequence" we extract the query, run
 *   Brave Search, append the results, and continue the conversation.
 */

import Anthropic from "@anthropic-ai/sdk";
import { EXTRACTING_PROMPT, RETRIEVAL_PROMPT, ANSWER_PROMPT } from "./prompts";
import { BraveSearchTool } from "./search";

// ---------------------------------------------------------------------------
// Env shape — the subset of wrangler.toml vars/secrets we use here
// ---------------------------------------------------------------------------

export interface CheckerEnv {
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  ANTHROPIC_SEARCH_MODEL: string;
  ANTHROPIC_SUMMARIZE_MODEL: string;
  ANTHROPIC_SEARCH_MAX_TOKENS: string;
  ANTHROPIC_ANSWER_MAX_TOKENS: string;
  N_SEARCH_RESULTS: string;
  MAX_SEARCHES: string;
}

// ---------------------------------------------------------------------------
// Helper: extract text between XML tags (port of extract_between_tags)
// ---------------------------------------------------------------------------

/**
 * Extract the last occurrence of text between <tag>…</tag>.
 * Mirrors ClientWithRetrieval.extract_between_tags() in the Python code.
 */
function extractBetweenTags(
  tag: string,
  text: string,
  strip = true
): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs");
  const matches: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = regex.exec(text)) !== null) {
    matches.push(strip ? (m[1] ?? "").trim() : (m[1] ?? ""));
  }
  return matches.length > 0 ? (matches[matches.length - 1] ?? null) : null;
}

// ---------------------------------------------------------------------------
// extractStatements
// ---------------------------------------------------------------------------

/**
 * Use Claude to extract factual statements from article text.
 *
 * Returns the raw Claude response (which includes <statement> and
 * <number_of_statements> tags that the retrieve loop consumes).
 *
 * Port of ClientWithRetrieval.extract_statements().
 */
export async function extractStatements(
  text: string,
  client: Anthropic,
  model: string,
  maxTokens: number
): Promise<string> {
  const message = await client.messages.create({
    model,
    max_tokens: maxTokens,
    temperature: 0,
    system: EXTRACTING_PROMPT,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: `<text>${text}</text>` }],
      },
    ],
  });

  const block = message.content[0];
  if (!block || block.type !== "text") {
    throw new Error("extractStatements: unexpected response from Claude");
  }
  return block.text;
}

// ---------------------------------------------------------------------------
// retrieve
// ---------------------------------------------------------------------------

/**
 * Iterative retrieval loop: Claude fact-checks each statement by issuing
 * <search_query> tags; we intercept those, run Brave Search, and feed results
 * back into the conversation.
 *
 * Port of ClientWithRetrieval.retrieve().
 *
 * @param articleText      Raw article text (used to extract statements first)
 * @param client           Anthropic client
 * @param searchTool       Brave search tool
 * @param model            Claude model string
 * @param maxTokens        Max tokens per Claude call
 * @param nSearchResults   How many Brave results to use per query
 * @param maxSearches      Upper bound on search iterations
 */
export async function retrieve(
  articleText: string,
  client: Anthropic,
  searchTool: BraveSearchTool,
  model: string,
  maxTokens: number,
  nSearchResults: number,
  maxSearches: number
): Promise<string> {
  // Step 1: Extract statements from the article
  const statements = await extractStatements(
    articleText,
    client,
    model,
    maxTokens
  );

  // Parse how many statements were extracted so we know how many searches to
  // attempt at most (mirrors the Python: min(num_of_statements, max_searches_to_try))
  const numStatementsStr = extractBetweenTags("number_of_statements", statements, true);
  const numStatements = numStatementsStr ? parseInt(numStatementsStr, 10) : maxSearches;
  const iterations = Math.min(
    isNaN(numStatements) ? maxSearches : numStatements,
    maxSearches
  );

  // Step 2: Build the retrieval system prompt
  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT
    .replace("{current_time}", currentTime)
    .replace("{description}", searchTool.toolDescription);

  // The conversation starts with the extracted statements as the user turn.
  // As Claude emits partial completions, we append them to this same message
  // content — mirroring the Python: messages[0]['content'][0]['text'] += ...
  let conversationText = statements;
  let completions = "";

  for (let attempt = 0; attempt < iterations; attempt++) {
    const message = await client.messages.create({
      model,
      max_tokens: maxTokens,
      temperature: 0,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: [{ type: "text", text: conversationText }],
        },
      ],
      // The critical stop sequence: Claude emits </search_query> when it wants
      // to search, allowing us to intercept and inject results.
      stop_sequences: ["</search_query>"],
    });

    const block = message.content[0];
    const partialCompletion = block && block.type === "text" ? block.text : "";
    completions += partialCompletion;
    conversationText += partialCompletion;

    if (
      message.stop_reason === "stop_sequence" &&
      message.stop_sequence === "</search_query>"
    ) {
      // Claude wants to search — extract the query it produced
      const searchQuery = extractBetweenTags(
        "search_query",
        partialCompletion + "</search_query>"
      );

      if (!searchQuery) {
        console.warn(
          `retrieve: could not extract search_query from partial completion at attempt ${attempt}`
        );
        // Append the closing tag and continue; Claude will hopefully recover
        completions += "</search_query>";
        conversationText += "</search_query>";
        continue;
      }

      console.log(
        `retrieve: search attempt ${attempt + 1}/${iterations} — query: "${searchQuery}"`
      );

      // Run the search and format results in the <search_results> envelope
      const formattedResults = await searchTool.searchFormatted(
        searchQuery,
        nSearchResults
      );

      // Append the closing tag + search results so Claude can continue
      completions += "</search_query>" + formattedResults;
      conversationText += "</search_query>" + formattedResults;
    } else {
      // Claude finished without requesting another search
      break;
    }
  }

  return completions;
}

// ---------------------------------------------------------------------------
// answerWithResults
// ---------------------------------------------------------------------------

/**
 * Generate the final editor's report from accumulated fact-checking results.
 *
 * Port of ClientWithRetrieval.answer_with_results().
 *
 * @param searchResults  The accumulated retrieval loop output
 * @param articleText    The original article text
 * @param client         Anthropic client
 * @param model          Claude model string
 * @param maxTokens      Max tokens for the answer
 */
export async function answerWithResults(
  searchResults: string,
  articleText: string,
  client: Anthropic,
  model: string,
  maxTokens: number
): Promise<string> {
  const prompt = `<fact_checking_results>${searchResults}</fact_checking_results> <text>${articleText}</text>`;

  const message = await client.messages.create({
    model,
    max_tokens: maxTokens,
    temperature: 0,
    system: ANSWER_PROMPT,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: prompt }],
      },
    ],
  });

  const block = message.content[0];
  const rawAnswer = block && block.type === "text" ? block.text : "";

  // Extract the content inside <answer>…</answer> tags (mirrors the Python)
  const extracted = extractBetweenTags("answer", rawAnswer);
  return extracted ?? rawAnswer;
}

// ---------------------------------------------------------------------------
// fullCheck — orchestrates the entire pipeline
// ---------------------------------------------------------------------------

/**
 * Run the complete article QA pipeline for a single article text.
 *
 * Returns the final markdown report ready to be posted as a GitHub comment.
 */
export async function fullCheck(
  articleText: string,
  env: CheckerEnv
): Promise<string> {
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });

  const { BRAVE_API_KEY } = env;
  const { toolDescription } = await import("./prompts").then((m) => ({
    toolDescription: m.BRAVE_DESCRIPTION,
  }));

  const searchTool = new BraveSearchTool(BRAVE_API_KEY, toolDescription);

  const searchModel = env.ANTHROPIC_SEARCH_MODEL;
  const maxTokens = parseInt(env.ANTHROPIC_SEARCH_MAX_TOKENS, 10) || 4000;
  const answerMaxTokens = parseInt(env.ANTHROPIC_ANSWER_MAX_TOKENS, 10) || 4096;
  const nSearchResults = parseInt(env.N_SEARCH_RESULTS, 10) || 3;
  const maxSearches = parseInt(env.MAX_SEARCHES, 10) || 5;

  // Step 1+2: Extract statements and run the retrieval / fact-check loop
  const factCheckResults = await retrieve(
    articleText,
    client,
    searchTool,
    searchModel,
    maxTokens,
    nSearchResults,
    maxSearches
  );

  // Step 3: Generate the final report
  const report = await answerWithResults(
    factCheckResults,
    articleText,
    client,
    searchModel,
    answerMaxTokens
  );

  return report;
}
