import Anthropic from '@anthropic-ai/sdk'
import { searchWeb, formatSearchResults } from './brave-search.js'

const EXTRACT_PROMPT = `You are a fact-checking assistant. Extract all factual statements from the article text that can be verified.
Focus on: dates, numbers, organization names, amounts, specific events, and claims.
Wrap each statement in <statement> tags. Count the total in <number_of_statements> tags.

Example output:
<number_of_statements>3</number_of_statements>
<statement>The hack occurred on August 2, 2022</statement>
<statement>Approximately $190 million was stolen</statement>
<statement>The attacker exploited a reentrancy vulnerability</statement>`

const RETRIEVAL_PROMPT = `You are a research assistant performing fact-checking. For each factual statement, formulate a search query to verify it.
Write your search query inside <search_query> tags. After receiving search results, evaluate the statement as True, False, or Unverified.

For each statement provide:
<verdict>True|False|Unverified</verdict>
<source>URL or reference</source>
<explanation>Brief explanation of your finding</explanation>

Process one statement at a time.`

const ANSWER_PROMPT = `You are an editor reviewing a wiki article submission. Based on the fact-checking results and the article content, provide a comprehensive review.

Your review must include:

1. **Fact-Check Results** — For each verified statement, show:
   - :white_check_mark: for verified true statements
   - :x: for statements found to be false
   - :warning: for unverified statements
   Include the source and explanation for each.

2. **Editor's Notes** — Check for:
   - Grammar and spelling errors
   - Date format (should be: Month day, year)
   - Writing style consistency
   - Data-backed claims vs speculation

3. **Structure Check** — Verify the article has:
   - Proper Hugo frontmatter between --- delimiters
   - Required fields: date, entities, title
   - Appropriate section headers
   - Figure placeholders with valid filenames

4. **Overall Assessment** — Brief summary of article quality and required changes.

Format your response as a GitHub-flavored markdown comment suitable for posting on a pull request.
Wrap your complete review in <answer> tags.`

export async function runPipeline(
  articleText: string,
  anthropicKey: string,
  braveKey: string,
  maxSearches = 5
): Promise<string> {
  const client = new Anthropic({ apiKey: anthropicKey })

  // Step 1: Extract factual statements
  const extractionResp = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 2000,
    temperature: 0,
    messages: [{ role: 'user', content: `${EXTRACT_PROMPT}\n\n<article>\n${articleText}\n</article>` }],
  })

  const extractionText = extractionResp.content[0].type === 'text' ? extractionResp.content[0].text : ''
  const statements = extractStatements(extractionText)
  const numToCheck = Math.min(statements.length, maxSearches)

  // Step 2: Iterative search and verification
  let searchResults = ''

  for (let i = 0; i < numToCheck; i++) {
    const statement = statements[i]

    // Ask Claude for a search query
    const queryResp = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 200,
      temperature: 0,
      stop_sequences: ['</search_query>'],
      messages: [
        {
          role: 'user',
          content: `${RETRIEVAL_PROMPT}\n\nVerify this statement: "${statement}"\n\nFormulate a search query:`,
        },
      ],
    })

    const queryText = queryResp.content[0].type === 'text' ? queryResp.content[0].text : ''
    const query = extractTag(queryText, 'search_query')

    if (!query) continue

    // Perform Brave search
    const results = await searchWeb(query, braveKey, 3)
    const formattedResults = formatSearchResults(results)

    // Ask Claude to evaluate the statement against results
    const evalResp = await client.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 500,
      temperature: 0,
      messages: [
        {
          role: 'user',
          content:
            `Evaluate this statement based on search results:\n\n` +
            `<statement>${statement}</statement>\n\n` +
            `${formattedResults}\n\n` +
            `Provide: <verdict>True|False|Unverified</verdict>\n` +
            `<source>best matching URL</source>\n` +
            `<explanation>brief explanation</explanation>`,
        },
      ],
    })

    const evalText = evalResp.content[0].type === 'text' ? evalResp.content[0].text : ''
    const verdict = extractTag(evalText, 'verdict') || 'Unverified'
    const source = extractTag(evalText, 'source') || 'N/A'
    const explanation = extractTag(evalText, 'explanation') || ''

    const emoji =
      verdict.toLowerCase() === 'true'
        ? ':white_check_mark:'
        : verdict.toLowerCase() === 'false'
          ? ':x:'
          : ':warning:'

    searchResults += `${emoji} **${statement}**\n`
    searchResults += `   Verdict: ${verdict} | Source: ${source}\n`
    searchResults += `   ${explanation}\n\n`
  }

  // Step 3: Final comprehensive review
  const answerResp = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 4000,
    temperature: 0,
    messages: [
      {
        role: 'user',
        content:
          `${ANSWER_PROMPT}\n\n` +
          `<article>\n${articleText}\n</article>\n\n` +
          `<fact_check_results>\n${searchResults}\n</fact_check_results>`,
      },
    ],
  })

  const answerText = answerResp.content[0].type === 'text' ? answerResp.content[0].text : ''
  return extractTag(answerText, 'answer') || answerText
}

function extractStatements(text: string): string[] {
  const matches = text.matchAll(/<statement>([\s\S]*?)<\/statement>/g)
  return Array.from(matches, (m) => m[1].trim())
}

function extractTag(text: string, tag: string): string | null {
  const match = text.match(new RegExp(`<${tag}>([\\s\\S]*?)(?:<\\/${tag}>|$)`))
  return match ? match[1].trim() : null
}
