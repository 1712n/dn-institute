/**
 * Claude API client — direct fetch-based, no SDK dependency.
 * Mirrors the original bot's three-phase approach:
 *   1. Extract factual statements
 *   2. Retrieve/verify via search
 *   3. Generate final answer with editor's notes
 */

import { braveSearch, formatSearchResults } from "./brave";

const ANTHROPIC_API = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-sonnet-4-20250514";
const HAIKU_MODEL = "claude-3-5-haiku-20241022";

interface ClaudeMessage {
  role: string;
  content: string;
}

async function callClaude(
  apiKey: string,
  system: string,
  messages: ClaudeMessage[],
  maxTokens: number = 4096,
  temperature: number = 0,
  stopSequences?: string[],
  model: string = MODEL
): Promise<{ text: string; stopReason: string }> {
  const body: any = {
    model,
    max_tokens: maxTokens,
    temperature,
    system,
    messages: messages.map((m) => ({
      role: m.role,
      content: [{ type: "text", text: m.content }],
    })),
  };
  if (stopSequences?.length) body.stop_sequences = stopSequences;

  const res = await fetch(ANTHROPIC_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Claude API error ${res.status}: ${errText}`);
  }

  const data: any = await res.json();
  return {
    text: data.content?.[0]?.text ?? "",
    stopReason: data.stop_reason ?? "end_turn",
  };
}

function extractBetweenTags(tag: string, text: string): string | null {
  const regex = new RegExp(`<${tag}\\s?>(.*?)</${tag}\\s?>`, "gs");
  let last: string | null = null;
  let match;
  while ((match = regex.exec(text)) !== null) {
    last = match[1].trim();
  }
  return last;
}

// ── Prompts (ported from Python) ──

const EXTRACTING_PROMPT = `Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.`;

const RETRIEVAL_PROMPT = `Your timeline extends up to the current one -- {current_time}.
You are tasked with verifying the accuracy of a series of factual statements using a search engine. Below is the search engine's description: <tool_description>Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content.</tool_description>.
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
between the tags <source></source>. If there is no source, try to find a related link in the text between <text></text> tags and place this link in the "source" field. If there is no source at all put "None" in the "source" field.
If the verdict is True, put the symbol ":white_check_mark:" after the statement.
If the verdict is False, put the symbol ":x:" after the statement and also provide an explanation why.
If the verdict is Unverified or the link was taken from the text in <text></text> tags, put the symbol ":warning:" after the statement.
Output example:
- **Statement**: Squid Game: November 1, 2021 - $5.7m :x:
  - **Source**: [link](link)
  - **Explanation**: ...

2. Make detailed editor's notes on the text in <text></text> tags. 
Suggest stylistic and grammatical improvements and point out any error in the text between <text></text> tags. 
Please make sure that in the '## Timeline' section, dates are written in the correct format 'Month day, year, time PM UTC:'. 
Example: 'May 05, 2023, 05:52 PM UTC:'.
Put your detailed notes and the list of errors below the header. 
Output example:
## Editor's Notes
...

3. Additionally, since the text between <text></text> is a Markdown document for Hugo SSG, ensure it adheres to specific Markdown formatting requirements.
If it adheres, put the symbol ":white_check_mark:".
If does not adhere, put the symbol ":x:" and also provide an explanation why.
If you are not sure, put the symbol ":warning:".
Output example:
## Hugo SSG Formatting Check
- Does it match Hugo SSG formatting? :x:
  - **Explanation**: ...

4. Check if the text between <text></text> follows the Markdown format, including appropriate headers.
Confirm if it meets submission guidelines, particularly the file naming convention ("YYYY-MM-DD-entity-that-was-hacked.md"). Extract the name of the file from the text between <text></text> tags and compare it to the correct name.
Pay special attention to matching the dates and names in the filename with the dates and names from the text.
Verify that the text between <text></text> includes only the allowed headers: "## Summary", "## Attackers", "## Losses", "## Timeline", "## Security Failure Causes".
Check for the presence of specific metadata headers between "---" lines, such as "date", "target-entities", "entity-types", "attack-types", "title", "loss" in the text within <text></text> tags. It must contain all and only allowed metadata headers.

The 'date' metadata header must match the actual date of the event described within the <text></text> tags, possibly mentioned in the Summary section.
The 'target-entities' metadata header must contain the actual names of the affected entities.
The 'loss' metadata header must match the actual loss due the event described.
Ensure that the value of the 'entity-types' metadata header corresponds to the target entity.
Ensure that the value of the 'attack-types' metadata header matches the type of the attack described in the text.
Point out any discrepancies in the "Notes" field, place a ":warning:" symbol.

Output example:
## Filename Check
- Correct Filename: ...
- Your Filename: ... :white_check_mark:

## Section Headers Check
- Allowed Headers: ...
- Your Headers: ... :white_check_mark:

## Metadata Headers Check
- Allowed Metadata Headers: ...
- Your Metadata Headers: ...
- Notes: ...

Combine the results of all steps into a single output that complies with Markdown format and return it to me in <answer></answer> tags.`;

// ── Main pipeline ──

export async function checkArticle(
  text: string,
  anthropicKey: string,
  braveKey: string
): Promise<string> {
  // Phase 1: Extract statements
  const extractResult = await callClaude(
    anthropicKey,
    EXTRACTING_PROMPT,
    [{ role: "user", content: `<text>${text}</text>` }],
    4096,
    0,
    undefined,
    HAIKU_MODEL
  );

  const statements = extractResult.text;
  const numStr = extractBetweenTags("number_of_statements", statements);
  const numStatements = Math.min(parseInt(numStr ?? "5", 10), 10);

  // Phase 2: Retrieve & verify via search
  const currentTime = new Date().toISOString().slice(0, 19).replace("T", " ");
  const systemPrompt = RETRIEVAL_PROMPT.replace("{current_time}", currentTime);

  let conversation = statements;
  let completions = "";

  for (let i = 0; i < numStatements; i++) {
    const result = await callClaude(
      anthropicKey,
      systemPrompt,
      [{ role: "user", content: conversation }],
      4096,
      0,
      ["</search_query>"]
    );

    completions += result.text;
    conversation += result.text;

    if (result.stopReason === "stop_sequence" || result.text.includes("<search_query>")) {
      const query = extractBetweenTags("search_query", result.text + "</search_query>");
      if (query) {
        const searchResults = await braveSearch(query, braveKey, 5);
        const formatted = formatSearchResults(searchResults);
        completions += "</search_query>" + formatted;
        conversation += "</search_query>" + formatted;
      }
    } else {
      break;
    }
  }

  // Phase 3: Generate final answer
  const answerResult = await callClaude(
    anthropicKey,
    ANSWER_PROMPT,
    [
      {
        role: "user",
        content: `<fact_checking_results>${completions}</fact_checking_results> <text>${text}</text>`,
      },
    ],
    4096,
    0
  );

  return extractBetweenTags("answer", answerResult.text) ?? answerResult.text;
}
