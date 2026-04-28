/**
 * 🌰 LLM Integration for Article Checking
 * Uses Anthropic Claude for analysis and Brave Search for fact-checking
 */

export interface Env {
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
}

export interface LLMResponse {
  content: string;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
}

/**
 * Analyze article content with Claude
 */
export async function analyzeWithClaude(
  env: Env,
  articleText: string,
  systemPrompt: string
): Promise<LLMResponse> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 4096,
      system: systemPrompt,
      messages: [
        { role: 'user', content: articleText }
      ],
    }),
  });

  if (!response.ok) {
    throw new Error(`Claude API error: ${response.status}`);
  }

  const data = await response.json();
  return {
    content: data.content[0].text,
    usage: data.usage,
  };
}

/**
 * Search the web with Brave Search
 */
export async function searchWithBrave(
  env: Env,
  query: string,
  count: number = 5
): Promise<{ results: Array<{ title: string; url: string; snippet: string }> }> {
  const response = await fetch(
    `https://api.search.brave.com/resolver/v1/web/search?q=${encodeURIComponent(query)}&count=${count}`,
    {
      headers: {
        'Accept': 'application/json',
        'X-Subscription-Token': env.BRAVE_API_KEY,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Brave Search error: ${response.status}`);
  }

  const data = await response.json();
  return {
    results: data.web?.results?.map((r: { title: string; url: string; description: string }) => ({
      title: r.title,
      url: r.url,
      snippet: r.description,
    })) || [],
  };
}

/**
 * 🌰 Fact-check claims in article content
 */
export async function factCheckClaims(
  env: Env,
  claims: string[]
): Promise<Record<string, { verified: boolean; sources: string[] }> {
  const results: Record<string, { verified: boolean; sources: string[] }> = {};

  for (const claim of claims) {
    const search = await searchWithBrave(env, claim, 3);
    // Simple verification: if we found results, consider it potentially verifiable
    results[claim] = {
      verified: search.results.length > 0,
      sources: search.results.slice(0, 2).map(r => r.url),
    };
  }

  return results;
}