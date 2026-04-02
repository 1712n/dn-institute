/**
 * Article Checker Cloudflare Worker 🌰
 * 
 * Migrated from Python GitHub Actions workflow to TypeScript Cloudflare Worker
 * for automated PR quality checks on article submissions.
 * 
 * Fixes #425
 */

import { Hono } from 'hono';
import { Octokit } from '@octokit/rest';

// Environment bindings
interface Env {
  GITHUB_TOKEN: string;
  GITHUB_WEBHOOK_SECRET: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  WIKI_REVIEWERS: string; // JSON array of allowed reviewers
}

// GitHub webhook payload types
interface WebhookPayload {
  action: string;
  issue?: {
    pull_request?: {
      url: string;
      html_url: string;
    };
    number: number;
  };
  comment?: {
    body: string;
    user: {
      login: string;
    };
  };
  repository: {
    owner: {
      login: string;
    };
    name: string;
    full_name: string;
  };
}

// Diff parsing types
interface DiffHunk {
  header: string;
  body: Array<{
    body: string;
  }>;
}

// Prompts (migrated from Python client.py)
const EXTRACTING_PROMPT = `
Please extract important statements that appear to be factual from the text provided between <text></text> tags.
Return the extracted statements. Place each statement within <statement></statement> tags.
Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
Aim to extract important statements with numbers, dates, and names of organizations. There should not be too many extracted statements.
Skip the preamble; go straight into the result.
`;

const RETRIEVAL_PROMPT = `
Your timeline extends up to the current one - {current_time}.
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
`;

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
`;

const BRAVE_DESCRIPTION = `Brave Search Engine Tool: The search engine will search using the Brave search engine for web pages with keywords similar to your query. It returns for each page its title, a summary and potentially the full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic.`;

const app = new Hono<{ Bindings: Env }>();

/**
 * Verify GitHub webhook signature for security
 */
async function verifySignature(payload: string, signature: string, secret: string): Promise<boolean> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  const signed = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
  const expected = `sha256=${Array.from(new Uint8Array(signed)).map(b => b.toString(16).padStart(2, '0')).join('')}`;
  
  return signature === expected;
}

/**
 * Extract text between XML tags
 * Fixed to handle unclosed tags properly
 */
function extractBetweenTags(tag: string, text: string): string | null {
  // Match both closed and unclosed tags
  const regex = new RegExp(`<${tag}\\s?>([^<]*)(?:</${tag}\\s?>|$)`, 's');
  const match = text.match(regex);
  return match ? match[1].trim() : null;
}

/**
 * Parse diff content (migrated from Python git module)
 * Note: Already strips '+' prefix from added lines
 */
function parseDiff(diffText: string): DiffHunk[] {
  const hunks: DiffHunk[] = [];
  const lines = diffText.split('\n');
  
  let currentHunk: DiffHunk | null = null;
  let currentBody: string[] = [];
  
  for (const line of lines) {
    if (line.startsWith('diff --git')) {
      if (currentHunk) {
        hunks.push({
          header: currentHunk.header,
          body: [{ body: currentBody.join('\n') }]
        });
      }
      currentHunk = { header: line, body: [] };
      currentBody = [];
    } else if (currentHunk) {
      if (line.startsWith('+') && !line.startsWith('+++')) {
        // Strip '+' prefix when parsing
        currentBody.push(line.substring(1));
      }
    }
  }
  
  // Add last hunk
  if (currentHunk && currentBody.length > 0) {
    hunks.push({
      header: currentHunk.header,
      body: [{ body: currentBody.join('\n') }]
    });
  }
  
  return hunks;
}

/**
 * Call Brave Search API with timeout handling
 */
async function braveSearch(query: string, apiKey: string, timeoutMs: number = 10000): Promise<string> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(`https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=10`, {
      headers: {
        'Accept': 'application/json',
        'X-Subscription-Token': apiKey
      },
      signal: controller.signal
    });
    
    if (!response.ok) {
      throw new Error(`Brave API error: ${response.status}`);
    }
    
    const data = await response.json() as any;
    const results: string[] = [];
    
    // Process web results
    if (data.web?.results) {
      for (const result of data.web.results.slice(0, 3)) {
        results.push(`Web Page Title: ${result.title}\nWeb Page URL: ${result.url}\nWeb Page Description: ${result.description || ''}`);
      }
    }
    
    // Process news results
    if (data.news?.results) {
      for (const result of data.news.results.slice(0, 2)) {
        results.push(`News Article Title: ${result.title}\nNews Article Description: ${result.description || ''}\nNews Article Source: ${result.meta_url?.hostname || 'Unknown'}`);
      }
    }
    
    return results.join('\n\n');
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Brave API timeout');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Call Anthropic API for completion with timeout handling
 */
async function anthropicCompletion(
  systemPrompt: string,
  userContent: string,
  apiKey: string,
  model: string = 'claude-3-5-sonnet-20241022',
  maxTokens: number = 4000,
  temperature: number = 0,
  timeoutMs: number = 25000
): Promise<string> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model,
        max_tokens: maxTokens,
        temperature,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: [{ type: 'text', text: userContent }]
          }
        ]
      }),
      signal: controller.signal
    });
    
    if (!response.ok) {
      throw new Error(`Anthropic API error: ${response.status}`);
    }
    
    const data = await response.json() as any;
    return data.content[0].text;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Anthropic API timeout');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

    // Check if Claude wants to search (no need to add artificial closing tag)
    const searchQuery = extractBetweenTags('search_query', completion);
    if (searchQuery) {
      try {
        const results = await braveSearch(searchQuery, braveKey);
        completion = completion.replace('</search_query>', `</search_query>\n<search_result>\n${results}\n</search_result>`);
      } catch (error) {
        // If search fails, add error result and continue
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        completion = completion.replace('</search_query>', `</search_query>\n<search_result>\nSearch failed: ${errorMsg}\n</search_result>`);
      }
    } else {
      break;
    }

/**
 * Extract factual statements from text
 */
async function extractStatements(text: string, apiKey: string): Promise<string> {
  return anthropicCompletion(
    EXTRACTING_PROMPT,
    `<text>${text}</text>`,
    apiKey,
    'claude-3-5-sonnet-20241022',
    1000,
    0
  );
}

/**
 * Retrieve and fact-check statements
 */
async function retrieveAndCheck(
  statements: string,
  text: string,
  anthropicKey: string,
  braveKey: string,
  maxSearches: number = 5
): Promise<string> {
  const numStatements = parseInt(extractBetweenTags('number_of_statements', statements) || '1');
  const currentTime = new Date().toISOString().replace('T', ' ').substring(0, 19);
  
  let searchResults = '';
  let completion = statements;
  
  const searchCount = Math.min(numStatements, maxSearches);
  
  for (let i = 0; i < searchCount; i++) {
    const retrievalPrompt = RETRIEVAL_PROMPT
      .replace('{current_time}', currentTime)
      .replace('{description}', BRAVE_DESCRIPTION);
    
    const response = await anthropicCompletion(
      retrievalPrompt,
      completion,
      anthropicKey,
      'claude-3-5-sonnet-20241022',
      4000,
      0
    );
    
    completion = response;
    
/**
 * Parse PR URL to extract owner, repo, and PR number
 * Handles both API and HTML URL formats:
 * - https://api.github.com/repos/owner/repo/pulls/123
 * - https://github.com/owner/repo/pull/123
 */
function parsePullRequestUrl(url: string): { owner: string; repo: string; prNumber: number } | null {
  // Try to match both formats
  const patterns = [
    // API format: https://api.github.com/repos/owner/repo/pulls/123
    /https?:\/\/api\.github\.com\/repos\/([^\/]+)\/([^\/]+)\/pulls\/(\d+)/,
    // HTML format: https://github.com/owner/repo/pull/123
    /https?:\/\/github\.com\/([^\/]+)\/([^\/]+)\/pull\/(\d+)/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) {
      return {
        owner: match[1],
        repo: match[2],
        prNumber: parseInt(match[3])
      };
    }
  }
  
  return null;
}
  }
  
  return completion;
}

/**
 * Generate final answer with fact-checking results
 */
async function generateAnswer(
  factCheckResults: string,
  originalText: string,
  apiKey: string
): Promise<string> {
  const prompt = `<fact_checking_results>${factCheckResults}</fact_checking_results> <text>${originalText}</text>`;
  
  const response = await anthropicCompletion(
    ANSWER_PROMPT,
    prompt,
    apiKey,
    'claude-3-5-sonnet-20241022',
    4000,
    0
  );
  
  return extractBetweenTags('answer', response) || response;
}

/**
 * Main article checking logic
 */
async function checkArticle(
  pullUrl: string,
  githubToken: string,
  anthropicKey: string,
  braveKey: string
): Promise<string> {
  const octokit = new Octokit({ auth: githubToken });
  
  // Parse PR URL to get owner, repo, and PR number
  const parsed = parsePullRequestUrl(pullUrl);
  if (!parsed) {
    throw new Error(`Invalid PR URL format: ${pullUrl}`);
  }
  
  const { owner, repo, prNumber } = parsed;
  
  // Get PR diff using octokit.pulls.listFiles() for structured data
  const { data: files } = await octokit.pulls.listFiles({
    owner,
    repo,
    pull_number: prNumber
  });
  
  if (files.length === 0) {
    return 'No changes found in the PR.';
  }
  
  // Build diff text from structured file data
  const diffText = files.map(file => file.patch || '').join('\n');
  
  // Parse diff (already strips '+' prefix)
  const diff = parseDiff(diffText);
  
  if (diff.length === 0) {
    return 'No changes found in the PR.';
  }
  
  // Get the article text directly from parsed diff (no removePlus needed - parseDiff already strips it)
  const articleText = diff[0].header + diff[0].body[0].body;
  
  // Step 1: Extract factual statements
  const statements = await extractStatements(articleText, anthropicKey);
  
  // Step 2: Retrieve and fact-check
  const factCheckResults = await retrieveAndCheck(statements, articleText, anthropicKey, braveKey);
  
  // Step 3: Generate final answer
  const answer = await generateAnswer(factCheckResults, articleText, anthropicKey);
  
  return answer;
}

/**
 * Post comment on PR
 */
async function postComment(
  owner: string,
  repo: string,
  issueNumber: number,
  comment: string,
  githubToken: string
): Promise<void> {
  const octokit = new Octokit({ auth: githubToken });
  
  await octokit.issues.createComment({
    owner,
    repo,
    issue_number: issueNumber,
    body: comment
  });
}

/**
 * Check if user is in allowed reviewers list
 */
function isAllowedReviewer(username: string, reviewersJson: string): boolean {
  try {
    const reviewers = JSON.parse(reviewersJson);
    return reviewers.includes(username);
  } catch {
    return false;
  }
}

// Health check endpoint
app.get('/', (c) => {
  return c.json({ 
    status: 'ok', 
    service: 'Article Checker Worker 🌰',
    version: '1.0.0'
  });
});

// GitHub webhook handler
app.post('/webhook', async (c) => {
  const signature = c.req.header('X-Hub-Signature-256') || '';
  const payload = await c.req.text();
  
  // Verify webhook signature
  const isValid = await verifySignature(payload, signature, c.env.GITHUB_WEBHOOK_SECRET);
  if (!isValid) {
    return c.json({ error: 'Invalid signature' }, 401);
  }
  
  const data: WebhookPayload = JSON.parse(payload);
  
  // Check if this is a PR comment with /articlecheck command
  if (
    data.action === 'created' &&
    data.issue?.pull_request &&
    data.comment?.body.includes('/articlecheck')
  ) {
    // Check permissions
    if (!isAllowedReviewer(data.comment.user.login, c.env.WIKI_REVIEWERS)) {
      return c.json({ error: 'Permission denied' }, 403);
    }
    
    // Run article check asynchronously
    c.executionCtx.waitUntil(
      (async () => {
        try {
          const result = await checkArticle(
            data.issue!.pull_request!.html_url, // Use html_url which is what webhooks provide
            c.env.GITHUB_TOKEN,
            c.env.ANTHROPIC_API_KEY,
            c.env.BRAVE_API_KEY
          );
          
          // Post comment with results
          await postComment(
            data.repository.owner.login,
            data.repository.name,
            data.issue!.number,
            result,
            c.env.GITHUB_TOKEN
          );
        } catch (error) {
          console.error('Article check failed:', error);
          
          // Post error comment
          await postComment(
            data.repository.owner.login,
            data.repository.name,
            data.issue!.number,
            `❌ Article check failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
            c.env.GITHUB_TOKEN
          );
        }
      })()
    );
    
    return c.json({ status: 'Processing', message: 'Article check initiated' });
  }
  
  return c.json({ status: 'Ignored', message: 'Not an article check request' });
});

// Manual trigger endpoint (for testing)
app.post('/check', async (c) => {
  const body = await c.req.json<{ pull_url: string }>();
  
  if (!body.pull_url) {
    return c.json({ error: 'pull_url required' }, 400);
  }
  
  try {
    const result = await checkArticle(
      body.pull_url,
      c.env.GITHUB_TOKEN,
      c.env.ANTHROPIC_API_KEY,
      c.env.BRAVE_API_KEY
    );
    
    return c.json({ result });
  } catch (error) {
    return c.json({ 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, 500);
  }
});

export default app;
