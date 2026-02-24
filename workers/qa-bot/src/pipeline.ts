/**
 * Article QA Pipeline — 3-phase check migrated from the Python bot.
 *
 * Phase 1: Extract factual statements from article text (Claude Haiku — fast)
 * Phase 2: Iterative fact verification via Brave Search (Claude Sonnet)
 * Phase 3: Comprehensive review generation (fact-check + editor + Hugo + metadata)
 */

import { callClaude } from "./llm";
import { braveSearch } from "./search";

// ---------------------------------------------------------------------------
// Models — Haiku for extraction (cheap/fast), Sonnet for reasoning
// ---------------------------------------------------------------------------

const EXTRACTION_MODEL = "claude-3-haiku-20240307";
const REASONING_MODEL = "claude-3-5-sonnet-20241022";
const MAX_SEARCHES = 5;

// ---------------------------------------------------------------------------
// Prompts — ported verbatim from the Python codebase
// ---------------------------------------------------------------------------

const EXTRACTING_PROMPT = `Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.`;

const RETRIEVAL_PROMPT = `Your timeline extends up to the current one — {current_time}.
You are tasked with verifying the accuracy of a series of factual statements using a search engine. Below is the search engine's description: <tool_description>Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic.</tool_description>.
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
`;

const ANSWER_PROMPT = `You are an editor. Perform the following tasks:
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
`;

// ---------------------------------------------------------------------------
// Pipeline
// ---------------------------------------------------------------------------

/**
 * Run the full 3-phase article quality check.
 */
export async function runArticleCheck(
  filename: string,
  articleText: string,
  llmApiKey: string,
  searchApiKey: string
): Promise<string> {
  // Phase 1 — Extract factual statements
  const statements = await callClaude({
    apiKey: llmApiKey,
    model: EXTRACTION_MODEL,
    system: EXTRACTING_PROMPT,
    userMessage: `<text>${articleText}</text>`,
    maxTokens: 1000,
    temperature: 0,
  });

  // Parse number of statements
  const numMatch = statements.match(
    /<number_of_statements>\s*(\d+)\s*<\/number_of_statements>/
  );
  const numStatements = numMatch ? parseInt(numMatch[1], 10) : 3;
  const maxSearches = Math.min(numStatements, MAX_SEARCHES);

  // Phase 2 — Iterative fact verification with search
  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT.replace("{current_time}", currentTime);

  let conversation = statements;
  for (let i = 0; i < maxSearches; i++) {
    const partial = await callClaude({
      apiKey: llmApiKey,
      model: REASONING_MODEL,
      system: systemPrompt,
      userMessage: conversation,
      maxTokens: 4000,
      temperature: 0,
      stopSequences: ["</search_query>"],
    });

    conversation += partial;

    // Check if model issued a search query
    const queryMatch = partial.match(
      /<search_query>([\s\S]*?)(?:<\/search_query>)?$/
    );
    if (queryMatch) {
      const query = queryMatch[1].trim();
      const results = await braveSearch(query, searchApiKey);
      conversation += "</search_query>" + formatSearchResults(results);
    } else {
      break; // Model finished without needing more searches
    }
  }

  // Phase 3 — Comprehensive review
  const reviewPrompt = `<fact_checking_results>${conversation}</fact_checking_results> <text>${articleText}</text>`;
  const review = await callClaude({
    apiKey: llmApiKey,
    model: REASONING_MODEL,
    system: ANSWER_PROMPT,
    userMessage: reviewPrompt,
    maxTokens: 4000,
    temperature: 0,
  });

  // Extract answer from tags
  const answerMatch = review.match(/<answer>([\s\S]*?)<\/answer>/);
  const answer = answerMatch ? answerMatch[1].trim() : review;

  return `## QA Bot Review — \`${filename}\`\n\n${answer}`;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

interface SearchResult {
  title: string;
  url: string;
  description: string;
}

function formatSearchResults(results: SearchResult[]): string {
  if (results.length === 0) {
    return "<search_result>No results found.</search_result>";
  }
  const formatted = results
    .map(
      (r) =>
        `Web Page Title: ${r.title}\nWeb Page URL: ${r.url}\nWeb Page Description: ${r.description}`
    )
    .join("\n\n");
  return `<search_result>\n${formatted}\n</search_result>`;
}
