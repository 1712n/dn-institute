/**
 * 🌰 Three-phase fact-checking pipeline
 *
 * Phase 1: Statement extraction (Claude)
 * Phase 2: Iterative fact-checking via Brave Search (up to 5 rounds)
 * Phase 3: Comprehensive review (fact-checks + editor notes + Hugo SSG check + metadata)
 *
 * Ported verbatim from tools/article_checker/claude_retriever/client.py
 */

import { callClaude, SEARCH_MODEL } from "./llm"
import { braveSearch, formatSearchResults, BRAVE_DESCRIPTION } from "./search"

// ─── Prompts (ported from Python) ────────────────────────────────────────────

const EXTRACTING_PROMPT = `
Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.
`.trim()

const RETRIEVAL_PROMPT = `
Your timeline extends up to the current one — {current_time}.
You are tasked with verifying the accuracy of a series of factual statements using a search engine. Below is the search engine's description: <tool_description>{description}</tool_description>.
For each statement within <statement></statement> tags, if the statement already has a verdict in the <verdict></verdict> tags (either 'True' or 'False'), skip it and move to the next statement. For statements without a verdict, formulate a query to check its accuracy. You can make a call to the search engine tool by inserting a query within <search_query> tags like so: <search_query>query</search_query>. You'll then get results back within <search_result></search_result> tags.
Based on these results, determine the accuracy of each statement and categorize it as 'True', 'False', or 'Unverified'.
Put your verdict in <verdict></verdict> tags. If a statement is true, put 'True' in the <verdict></verdict> tags.
Include the Web Page URL in <source></source> tags. If there is no URL at all, put 'None' in the <source></source> tags.
If a statement is false, include an explanation in <explanation></explanation> tags.
Focus particularly on verifying numbers, dates, monetary values, and names of people or organizations.
Avoid verifying statements that already have a True/False verdict in the <verdict></verdict> tags.
Determine the accuracy of each statement using only information that is contained in the search_result.
If you need to search again, put the new query in <search_query></search_query>.

Statements to be verified:
`.trim()

const ANSWER_PROMPT = `
You are an editor. Perform the following tasks:
1. Using the information provided within the <fact_checking_results></fact_checking_results> tags,
please form the desired output with results of fact-checking.
List each statement from the tags <statement></statement> and accompany it with the fact-checking source
between the tags <source></source>.  If there is no source, try to find a related link in the text between <text></text> tags and place this link in the "source" field. If there is no source at all put "None" in the "source" field.
If the verdict is True, put the symbol ":white_check_mark:" after the statement.
If the verdict is False, put the symbol ":x:" after the statement and also provide an explanation why.
If the verdict is Unverified or the link was taken from the text in <text></text> tags, put the symbol ":warning:" after the statement.
Output example:
'''- **Statement**: Squid Game: November 1, 2021 - $5.7m :x:
  - **Source**: [https://www.wired.co.uk/article/squid-game-crypto-scam](https://www.wired.co.uk/article/squid-game-crypto-scam)
  - **Explanation**: The article states the Squid Game crypto scam creators pulled out $3.36 million on November 1, 2021, not $5.7 million as the statement claims.'''

2. Make detailed editor's notes on the text in <text></text> tags.
Suggest stylistic and grammatical improvements and point out any error in the text between <text></text> tags.
Please make sure that in the '## Timeline' section, dates are written in the correct format 'Month day, year, time PM UTC:'.
Example: 'May 05, 2023, 05:52 PM UTC:'.
Put your detailed notes and the list of errors below the header.
Output example:
'''## Editor's Notes
...'''

3. Additionally, since the text between <text></text> is a Markdown document for Hugo SSG, ensure it adheres to specific Markdown formatting requirements.
If it adheres, put the symbol ":white_check_mark:".
If does not adhere, put the symbol ":x:" and also provide an explanation why.
If you are not sure, put the symbol ":warning:".
Output example:
'''## Hugo SSG Formatting Check
- Does it match Hugo SSG formatting? :x:
  - **Explanation**: ...'''

4. Check if the text between <text></text> follows the Markdown format, including appropriate headers.
Confirm if it meets submission guidelines, particularly the file naming convention ("YYYY-MM-DD-entity-that-was-hacked.md"). Extract the name of the file from the text between <text></text> tags and compare it to the correct name.
Pay special attention to matching the dates and names in the filename with the dates and names from the text.
Verify that the text between <text></text> includes only the allowed headers: "## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes".
Check for the presence of specific metadata headers between "---" lines, such as "date", "target-entities", "entity-types", "attack-types", "title", "loss" in the text within <text></text> tags. It must contain all and only allowed metadata headers.

The 'date' metadata header must match the actual date of the event described within the <text></text> tags, possibly mentioned in the Summary section.
To achieve this, search for dates within the text to identify the occurrence date of the event.
Then, place this date within the <thinking></thinking> tags. Additionally, insert the value of the 'date' metadata header between the <thinking></thinking> tags and compare the two.
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

The 'target-entities' metadata header must contain the actual names of the affected entities during the event described in the <text></text> tags, possibly mentioned in the Summary section.
To achieve this, perform a text search to identify the target entities. Then place these entities in <thinking></thinking> tags. Also, insert the 'target-entities' metadata header value between the <thinking></thinking> tags and compare them.
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

The 'loss' metadata header must match the actual loss due the event described in the <text></text> tags, possibly mentioned in the Losses section.
To achieve this, perform a text search to identify the loss. Then place this loss in <thinking></thinking> tags. Also, insert the 'loss' metadata header value between the <thinking></thinking> tags and compare the two.
Please approach this task step by step. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Ensure that the value of the 'entity-types' metadata header corresponds to the target entity. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Ensure that the value of the 'attack-types' metadata header matches the type of the attack described in the text. Point out the discrepancies in the "Notes" field, place a ":warning:" symbol.

Output example:
'''## Filename Check
- Correct Filename: \`2022-02-15-ValentineFloki.md\`
- Your Filename: \`scam.md\` :x:

## Section Headers Check
- Allowed Headers: \`## Summary, ## Attackers, ## Losses, ## Timeline, ## Security Failure Causes\`
- Your Headers: \`# Cryptocurrency Scam Types and Prevention Measures, ## 1. Rug Pull, ### Overview, ### Recognition Tips, ## 2. Honeypot, ### Overview, ### Recognition Tips\` :x:

## Metadata Headers Check
- Allowed Metadata Headers: \`date, target-entities, entity-types, attack-types, title, loss\`
- Your Metadata Headers: \`date, target-entities, entity-types\` :x:
- Notes:
    - The \`date\` header has an incorrect date. It lists 2022-03-15, whereas it should be 2022-02-15 ":warning:"
    - The \`loss\` header displays an incorrect value. It shows $100, whereas it should indicate $1000. ":warning:"
'''

Combine the results of all steps into a single output that complies with Markdown format and return it to me in <answer></answer> tags.
`.trim()

// ─── Pipeline ────────────────────────────────────────────────────────────────

/**
 * Run the full 3-phase article checking pipeline.
 */
export async function runPipeline(
  articleText: string,
  apiKey: string,
  braveApiKey: string
): Promise<string> {
  // Phase 1: Extract statements
  console.log("🌰 Phase 1: Extracting factual statements...")
  const statements = await extractStatements(articleText, apiKey)

  // Phase 2: Iterative fact-checking with search
  console.log("🌰 Phase 2: Fact-checking via Brave Search...")
  const factCheckResults = await factCheckWithSearch(
    statements,
    apiKey,
    braveApiKey
  )

  // Phase 3: Comprehensive review
  console.log("🌰 Phase 3: Generating comprehensive review...")
  const review = await generateReview(
    factCheckResults,
    articleText,
    apiKey
  )

  return review
}

/**
 * Phase 1: Extract factual statements from the article text.
 */
export async function extractStatements(
  text: string,
  apiKey: string
): Promise<string> {
  const response = await callClaude({
    apiKey,
    model: SEARCH_MODEL,
    system: EXTRACTING_PROMPT,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: `<text>${text}</text>` }],
      },
    ],
    maxTokens: 1000,
    temperature: 0.0,
  })

  return response.content[0].text
}

/**
 * Phase 2: Iteratively fact-check statements using Brave Search.
 * Claude issues search queries via stop sequences, we execute them and feed back results.
 */
export async function factCheckWithSearch(
  statements: string,
  apiKey: string,
  braveApiKey: string,
  maxSearches: number = 5
): Promise<string> {
  const numStatements = extractNumberOfStatements(statements)
  const currentTime = new Date().toISOString().replace("T", " ").substring(0, 19)
  const systemPrompt = RETRIEVAL_PROMPT
    .replace("{current_time}", currentTime)
    .replace("{description}", BRAVE_DESCRIPTION)

  let completions = ""
  let userText = statements

  const maxRounds = Math.min(numStatements, maxSearches)

  for (let i = 0; i < maxRounds; i++) {
    const response = await callClaude({
      apiKey,
      model: SEARCH_MODEL,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: [{ type: "text", text: userText }],
        },
      ],
      maxTokens: 4000,
      temperature: 0.0,
      stopSequences: ["</search_query>"],
    })

    const partialCompletion = response.content[0].text
    completions += partialCompletion
    userText += partialCompletion

    if (
      response.stop_reason === "stop_sequence" &&
      response.stop_sequence === "</search_query>"
    ) {
      // Extract search query and execute it
      const searchQuery = extractBetweenTags("search_query", partialCompletion + "</search_query>")
      if (!searchQuery) break

      console.log(`  Search round ${i + 1}: "${searchQuery}"`)
      const searchResults = await braveSearch(searchQuery, braveApiKey, 1)
      const formattedResults = formatSearchResults(
        searchResults.map((r) => r.content)
      )

      completions += "</search_query>" + formattedResults
      userText += "</search_query>" + formattedResults
    } else {
      // Claude finished without another search query
      break
    }
  }

  return completions
}

/**
 * Phase 3: Generate the comprehensive review with fact-checking results.
 */
export async function generateReview(
  factCheckResults: string,
  articleText: string,
  apiKey: string
): Promise<string> {
  const prompt = `<fact_checking_results>${factCheckResults}</fact_checking_results> <text>${articleText}</text>`

  const response = await callClaude({
    apiKey,
    model: SEARCH_MODEL,
    system: ANSWER_PROMPT,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: prompt }],
      },
    ],
    maxTokens: 4000,
    temperature: 0.0,
  })

  const fullAnswer = response.content[0].text
  return extractBetweenTags("answer", fullAnswer) ?? fullAnswer
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Extract content between XML-style tags. Returns the last match.
 */
export function extractBetweenTags(
  tag: string,
  text: string
): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs")
  const matches = [...text.matchAll(regex)]
  if (matches.length === 0) return null
  return matches[matches.length - 1][1].trim()
}

/**
 * Extract the number of statements from Claude's Phase 1 output.
 */
function extractNumberOfStatements(text: string): number {
  const num = extractBetweenTags("number_of_statements", text)
  if (num) {
    const parsed = parseInt(num, 10)
    if (!isNaN(parsed)) return parsed
  }
  // Fallback: count <statement> tags
  const matches = text.match(/<statement>/g)
  return matches?.length ?? 5
}

/**
 * Format search result content strings into XML structure.
 * (Overload that accepts string[] for the pipeline)
 */
function formatSearchResults(contents: string[]): string {
  const items = contents
    .map(
      (content, i) =>
        `<item index="${i + 1}">\n<page_content>\n${content}\n</page_content>\n</item>`
    )
    .join("\n")
  return `\n<search_results>\n${items}\n</search_results>`
}
