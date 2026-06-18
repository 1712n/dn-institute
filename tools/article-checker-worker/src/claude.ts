import type { ClaudeResponse } from "./types"
import { EXTRACTING_PROMPT, RETRIEVAL_PROMPT, ANSWER_PROMPT } from "./prompts"
import { braveSearch, formatSearchResults, BRAVE_DESCRIPTION } from "./search"

/** Model configuration matching config.json */
const SEARCH_MODEL = "claude-3-opus-20240229"
const SEARCH_MAX_TOKENS = 4000
const SEARCH_TEMPERATURE = 0.0

/**
 * Call the Anthropic Messages API.
 */
async function callClaude(
  apiKey: string,
  model: string,
  system: string,
  messages: Array<{ role: string; content: Array<{ type: string; text: string }> }>,
  maxTokens: number,
  temperature: number,
  stopSequences?: string[]
): Promise<ClaudeResponse> {
  const body: Record<string, unknown> = {
    model,
    max_tokens: maxTokens,
    temperature,
    system,
    messages,
  }
  if (stopSequences && stopSequences.length > 0) {
    body.stop_sequences = stopSequences
  }

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Claude API error: ${response.status} - ${text}`)
  }

  return response.json() as Promise<ClaudeResponse>
}

/**
 * Extract the last match of text between XML-style tags.
 */
export function extractBetweenTags(
  tag: string,
  text: string,
  strip: boolean = true
): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs")
  const matches = [...text.matchAll(regex)]
  if (matches.length === 0) return null
  const lastMatch = matches[matches.length - 1][1]
  return strip ? lastMatch.trim() : lastMatch
}

/**
 * Step 1: Extract factual statements from article text.
 */
async function extractStatements(
  text: string,
  apiKey: string
): Promise<string> {
  const response = await callClaude(
    apiKey,
    SEARCH_MODEL,
    EXTRACTING_PROMPT,
    [{ role: "user", content: [{ type: "text", text: `<text>${text}</text>` }] }],
    SEARCH_MAX_TOKENS,
    SEARCH_TEMPERATURE
  )
  return response.content[0].text
}

/**
 * Step 2: Retrieve and fact-check statements using search.
 * Implements the iterative search loop from the Python client.
 */
async function retrieveAndVerify(
  query: string,
  apiKey: string,
  searchApiKey: string
): Promise<string> {
  const statements = await extractStatements(query, apiKey)

  const numStatements = parseInt(
    extractBetweenTags("number_of_statements", statements, true) || "5"
  )

  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19)
  const systemPrompt = RETRIEVAL_PROMPT.replace("{current_time}", currentTime).replace(
    "{description}",
    BRAVE_DESCRIPTION
  )

  let completions = ""
  let messageText = statements

  const maxSearches = Math.min(numStatements, 5)

  for (let tries = 0; tries < maxSearches; tries++) {
    const response = await callClaude(
      apiKey,
      SEARCH_MODEL,
      systemPrompt,
      [{ role: "user", content: [{ type: "text", text: messageText }] }],
      SEARCH_MAX_TOKENS,
      SEARCH_TEMPERATURE,
      ["</search_query>"]
    )

    const partialCompletion = response.content[0].text
    completions += partialCompletion
    messageText += partialCompletion

    if (
      response.stop_reason === "stop_sequence" &&
      response.stop_sequence === "</search_query>"
    ) {
      // Extract search query and perform search
      const searchQuery = extractBetweenTags(
        "search_query",
        partialCompletion + "</search_query>"
      )

      if (!searchQuery) {
        throw new Error("Failed to extract search query from Claude response")
      }

      console.log(`Search query #${tries + 1}: ${searchQuery}`)

      const searchResults = await braveSearch(searchQuery, searchApiKey, 3)
      const formattedResults = formatSearchResults(searchResults)

      completions += "</search_query>" + formattedResults
      messageText += "</search_query>" + formattedResults
    } else {
      break
    }
  }

  return completions
}

/**
 * Step 3: Generate the final answer with fact-checking results, editor's notes,
 * and formatting checks.
 */
async function answerWithResults(
  searchResults: string,
  query: string,
  apiKey: string
): Promise<string> {
  const prompt = `<fact_checking_results>${searchResults}</fact_checking_results> <text>${query}</text>`

  const response = await callClaude(
    apiKey,
    SEARCH_MODEL,
    ANSWER_PROMPT,
    [{ role: "user", content: [{ type: "text", text: prompt }] }],
    SEARCH_MAX_TOKENS,
    SEARCH_TEMPERATURE
  )

  return response.content[0].text
}

/**
 * Main article checking pipeline.
 * Orchestrates: statement extraction → fact-checking retrieval → final answer.
 */
export async function checkArticle(
  articleText: string,
  llmApiKey: string,
  searchApiKey: string
): Promise<string> {
  // Step 1 & 2: Retrieve and verify statements
  const searchResults = await retrieveAndVerify(
    articleText,
    llmApiKey,
    searchApiKey
  )

  // Step 3: Generate comprehensive answer
  const rawAnswer = await answerWithResults(searchResults, articleText, llmApiKey)

  // Extract the answer between tags
  const answer = extractBetweenTags("answer", rawAnswer)

  return answer || rawAnswer
}
