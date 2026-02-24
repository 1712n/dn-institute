/**
 * Claude (Anthropic Messages API) client using native fetch.
 * Zero external dependencies — uses the Cloudflare Workers fetch API.
 */

const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";

export interface ClaudeOptions {
  apiKey: string;
  model: string;
  system: string;
  userMessage: string;
  maxTokens: number;
  temperature: number;
  stopSequences?: string[];
}

export async function callClaude(opts: ClaudeOptions): Promise<string> {
  const body: Record<string, unknown> = {
    model: opts.model,
    max_tokens: opts.maxTokens,
    temperature: opts.temperature,
    system: opts.system,
    messages: [{ role: "user", content: opts.userMessage }],
  };

  if (opts.stopSequences && opts.stopSequences.length > 0) {
    body.stop_sequences = opts.stopSequences;
  }

  const res = await fetch(ANTHROPIC_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": opts.apiKey,
      "anthropic-version": ANTHROPIC_VERSION,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Claude API error ${res.status}: ${errText}`);
  }

  const data = (await res.json()) as {
    content: Array<{ type: string; text: string }>;
  };

  return data.content
    .filter((block) => block.type === "text")
    .map((block) => block.text)
    .join("");
}
