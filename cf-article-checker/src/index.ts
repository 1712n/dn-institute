/**
 * Cloudflare Worker: Article Checker QA Bot
 *
 * Migrated from Python GitHub Actions workflow (article-check-claude.yml).
 * Receives GitHub issue_comment webhooks, triggers on `/articlecheck`,
 * performs fact-checking via Claude + Brave Search, and posts review as PR comment.
 *
 * 🌰🌰🌰
 */

import { Hono } from "hono";

// ─── Types ───────────────────────────────────────────────────────────────────

type Env = {
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  REVIEWERS: string; // comma-separated GitHub usernames
  ANTHROPIC_MODEL: string;
  ANTHROPIC_MAX_TOKENS: string;
};

interface GitHubCommentEvent {
  action: string;
  comment: {
    body: string;
    user: { login: string };
    issue_url: string;
  };
  issue: {
    pull_request?: { url: string };
    number: number;
  };
  repository: {
    full_name: string;
  };
}

interface DiffFile {
  header: string;
  body: { header: string; body: string }[];
}

interface SearchResult {
  title: string;
  url: string;
  description: string;
}

// ─── Prompts ─────────────────────────────────────────────────────────────────

const EXTRACTING_PROMPT = `Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.`;

const RETRIEVAL_PROMPT = `Your timeline extends up to the current one — {current_time}.
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

Statements to be verified:`;

const ANSWER_PROMPT = `You are an editor. Perform the following tasks:
1. Using the information provided within the <fact_checking_results></fact_checking_results> tags,
please form the desired output with results of fact-checking.
List each statement from the tags <statement></statement> and accompany it with the fact-checking source
between the tags <source></source>. If there is no source, try to find a related link in the text between <text></text> tags and place this link in the "source" field. If there is no source at all put "None" in the "source" field.
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

Combine the results of all steps into a single output that complies with Markdown format and return it to me in <answer></answer> tags.`;

const SEARCH_TOOL_DESCRIPTION = `A web search engine that returns relevant results for a given query. Use it by providing a search query.`;

// ─── Utility Functions ───────────────────────────────────────────────────────

function extractBetweenTags(tag: string, text: string): string | null {
  const regex = new RegExp(`<${tag}\\\\s?>(.+?)</${tag}\\\\s?>`, "gs");
  const matches = [...text.matchAll(regex)];
  if (matches.length > 0) {
    return matches[matches.length - 1][1].trim();
  }
  return null;
}

function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => line.replace(/^\+/, ""))
    .join("\n");
}

// ─── GitHub API ──────────────────────────────────────────────────────────────

async function getDiffFromUrl(
  diffUrl: string,
  token: string
): Promise<string> {
  const resp = await fetch(diffUrl, {
    headers: {
      Authorization: `token ${token}`,
      Accept: "application/vnd.github.v3.diff",
      "User-Agent": "cf-article-checker",
    },
  });
  if (!resp.ok) {
    throw new Error(`Failed to get diff: ${resp.status}`);
  }
  return resp.text();
}

function parseDiff(diff: string): DiffFile[] {
  const rawFiles = diff.split("diff --git ");
  rawFiles.shift(); // remove empty first element

  return rawFiles.map((rawFile) => {
    const rawSegments = rawFile.split("@@");
    const fileHeader = rawSegments.shift() || "";

    const segments: { header: string; body: string }[] = [];
    for (let i = 0; i < rawSegments.length; i += 2) {
      segments.push({
        header: rawSegments[i] || "",
        body: rawSegments[i + 1] || "",
      });
    }

    return { header: fileHeader, body: segments };
  });
}

async function postComment(
  repoFullName: string,
  issueNumber: number,
  body: string,
  token: string
): Promise<void> {
  const resp = await fetch(
    `https://api.github.com/repos/${repoFullName}/issues/${issueNumber}/comments`,
    {
      method: "POST",
      headers: {
        Authorization: `token ${token}`,
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "cf-article-checker",
      },
      body: JSON.stringify({ body }),
    }
  );
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Failed to post comment: ${resp.status} ${text}`);
  }
}

// ─── Anthropic Claude API ────────────────────────────────────────────────────

async function claudeMessages(
  system: string,
  messages: { role: string; content: string }[],
  apiKey: string,
  model: string,
  maxTokens: number,
  temperature: number = 0.0,
  stopSequences?: string[]
): Promise<{ text: string; stopReason: string; stopSequence: string | null }> {
  const body: Record<string, unknown> = {
    model,
    max_tokens: maxTokens,
    temperature,
    system,
    messages,
  };
  if (stopSequences?.length) {
    body.stop_sequences = stopSequences;
  }

  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const errorText = await resp.text();
    throw new Error(`Claude API error: ${resp.status} ${errorText}`);
  }

  const data = (await resp.json()) as {
    content: { type: string; text: string }[];
    stop_reason: string;
    stop_sequence: string | null;
  };

  return {
    text: data.content[0]?.text || "",
    stopReason: data.stop_reason,
    stopSequence: data.stop_sequence,
  };
}

// ─── Brave Search API ────────────────────────────────────────────────────────

async function braveSearch(
  query: string,
  apiKey: string,
  count: number = 3
): Promise<SearchResult[]> {
  const params = new URLSearchParams({ q: query, count: count.toString() });
  const resp = await fetch(
    `https://api.search.brave.com/res/v1/web/search?${params}`,
    {
      headers: {
        Accept: "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": apiKey,
      },
    }
  );

  if (!resp.ok) {
    throw new Error(`Brave Search error: ${resp.status}`);
  }

  const data = (await resp.json()) as {
    web?: { results: { title: string; url: string; description: string }[] };
  };

  return (data.web?.results || []).slice(0, count).map((r) => ({
    title: r.title,
    url: r.url,
    description: r.description,
  }));
}

function formatSearchResults(results: SearchResult[]): string {
  return results
    .map(
      (r, i) =>
        `<search_result>\n<title>${r.title}</title>\n<url>${r.url}</url>\n<description>${r.description}</description>\n</search_result>`
    )
    .join("\n");
}

// ─── Core Pipeline ───────────────────────────────────────────────────────────

async function extractStatements(
  text: string,
  apiKey: string,
  model: string,
  maxTokens: number
): Promise<{ statements: string; count: number }> {
  const result = await claudeMessages(
    EXTRACTING_PROMPT,
    [{ role: "user", content: `<text>${text}</text>` }],
    apiKey,
    model,
    maxTokens
  );

  const countStr = extractBetweenTags("number_of_statements", result.text);
  const count = countStr ? parseInt(countStr, 10) : 0;
  return { statements: result.text, count };
}

async function retrieveAndVerify(
  statements: string,
  apiKey: string,
  braveApiKey: string,
  model: string,
  maxTokens: number,
  maxSearches: number = 5,
  nSearchResults: number = 3
): Promise<string> {
  const currentTime = new Date().toISOString().replace("T", " ").slice(0, 19);
  const systemPrompt = RETRIEVAL_PROMPT
    .replace("{current_time}", currentTime)
    .replace("{description}", SEARCH_TOOL_DESCRIPTION);

  let completions = "";
  let messageContent = statements;

  for (let tries = 0; tries < maxSearches; tries++) {
    const result = await claudeMessages(
      systemPrompt,
      [{ role: "user", content: messageContent }],
      apiKey,
      model,
      maxTokens,
      0.0,
      ["</search_query>"]
    );

    completions += result.text;
    messageContent += result.text;

    if (
      result.stopReason === "stop_sequence" &&
      result.stopSequence === "</search_query>"
    ) {
      const searchQuery = extractBetweenTags(
        "search_query",
        result.text + "</search_query>"
      );
      if (!searchQuery) break;

      const searchResults = await braveSearch(searchQuery, braveApiKey, nSearchResults);
      const formattedResults = formatSearchResults(searchResults);
      const suffix = "</search_query>" + formattedResults;
      completions += suffix;
      messageContent += suffix;
    } else {
      break;
    }
  }

  return completions;
}

async function generateAnswer(
  searchResults: string,
  text: string,
  apiKey: string,
  model: string,
  maxTokens: number
): Promise<string> {
  const prompt = `<fact_checking_results>${searchResults}</fact_checking_results> <text>${text}</text>`;
  const result = await claudeMessages(
    ANSWER_PROMPT,
    [{ role: "user", content: prompt }],
    apiKey,
    model,
    maxTokens
  );

  return extractBetweenTags("answer", result.text) || result.text;
}

async function runArticleCheck(
  diffText: string,
  env: Env
): Promise<string> {
  const model = env.ANTHROPIC_MODEL || "claude-3-5-sonnet-20241022";
  const maxTokens = parseInt(env.ANTHROPIC_MAX_TOKENS || "4000", 10);
  const cleanedText = removePlus(diffText);

  // Step 1: Extract factual statements
  const { statements, count } = await extractStatements(
    cleanedText,
    env.ANTHROPIC_API_KEY,
    model,
    maxTokens
  );

  if (count === 0) {
    return `## Review\n\nNo factual statements were extracted from the article. The article may need more concrete data, dates, and figures.\n\n${statements}`;
  }

  // Step 2: Retrieve and verify via search
  const searchResults = await retrieveAndVerify(
    statements,
    env.ANTHROPIC_API_KEY,
    env.BRAVE_API_KEY,
    model,
    maxTokens
  );

  // Step 3: Generate final answer
  const answer = await generateAnswer(
    searchResults,
    cleanedText,
    env.ANTHROPIC_API_KEY,
    model,
    maxTokens
  );

  return answer;
}

// ─── Hono App ────────────────────────────────────────────────────────────────

const app = new Hono<{ Bindings: Env }>();

// Health check
app.get("/", (c) => c.text("🌰 Article Checker Worker is running"));

// GitHub webhook endpoint
app.post("/webhook", async (c) => {
  const event = c.req.header("X-GitHub-Event");
  if (event !== "issue_comment") {
    return c.json({ message: "Ignored event type" }, 200);
  }

  let payload: GitHubCommentEvent;
  try {
    payload = await c.req.json<GitHubCommentEvent>();
  } catch {
    return c.text("Invalid JSON", 400);
  }

  // Only handle created comments containing /articlecheck
  if (payload.action !== "created") {
    return c.json({ message: "Ignored action" }, 200);
  }

  if (!payload.comment.body.includes("/articlecheck")) {
    return c.json({ message: "No /articlecheck command" }, 200);
  }

  // Check if the commenter is an authorized reviewer
  const reviewers = (c.env.REVIEWERS || "")
    .split(",")
    .map((r) => r.trim().toLowerCase());
  const commenter = payload.comment.user.login.toLowerCase();

  if (!reviewers.includes(commenter)) {
    return c.json(
      { message: `User ${payload.comment.user.login} is not an authorized reviewer` },
      200
    );
  }

  // Verify this is a PR (not a regular issue)
  if (!payload.issue.pull_request) {
    return c.json({ message: "Not a pull request" }, 200);
  }

  const repoFullName = payload.repository.full_name;
  const issueNumber = payload.issue.number;

  // Use ctx.waitUntil for the long-running fact-checking process
  c.executionCtx.waitUntil(
    (async () => {
      try {
        // Get the PR diff
        const diffUrl = payload.issue.pull_request!.url + ".diff";
        const diff = await getDiffFromUrl(diffUrl, c.env.GITHUB_TOKEN);
        const parsedDiff = parseDiff(diff);

        if (parsedDiff.length === 0) {
          await postComment(
            repoFullName,
            issueNumber,
            "🌰 No diffable content found in this PR.",
            c.env.GITHUB_TOKEN
          );
          return;
        }

        // Run the article check pipeline on the first file's content
        const firstFile = parsedDiff[0];
        const diffContent =
          firstFile.header +
          firstFile.body.map((s) => s.header + s.body).join("");

        const review = await runArticleCheck(diffContent, c.env);

        // Post the review as a PR comment
        const commentBody = `## 🌰 Automated Article Review\n\n${review}\n\n---\n*Generated by [cf-article-checker](https://github.com/1712n/dn-institute/tree/main/cf-article-checker)*`;
        await postComment(repoFullName, issueNumber, commentBody, c.env.GITHUB_TOKEN);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        try {
          await postComment(
            repoFullName,
            issueNumber,
            `🌰 Article check failed: ${errorMsg}`,
            c.env.GITHUB_TOKEN
          );
        } catch {
          console.error("Failed to post error comment:", errorMsg);
        }
      }
    })()
  );

  return c.json({ message: "Article check triggered" }, 200);
});

export default app;
