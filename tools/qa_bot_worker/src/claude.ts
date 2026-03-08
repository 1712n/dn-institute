import type { ClaudeResponse } from "./types";

const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";

/**
 * Call Claude Messages API.
 */
export async function callClaude(
  systemPrompt: string,
  userMessage: string,
  apiKey: string,
  model: string,
  maxTokens: number,
  temperature: number = 0.0,
  stopSequences: string[] = []
): Promise<{ text: string; stopReason: string | null; stopSequence: string | null }> {
  const body: Record<string, unknown> = {
    model,
    max_tokens: maxTokens,
    temperature,
    system: systemPrompt,
    messages: [{ role: "user", content: userMessage }],
  };

  if (stopSequences.length > 0) {
    body.stop_sequences = stopSequences;
  }

  const response = await fetch(ANTHROPIC_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": ANTHROPIC_VERSION,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Claude API error: HTTP ${response.status} — ${errText}`);
  }

  const data = (await response.json()) as ClaudeResponse;

  const textBlock = data.content.find((c) => c.type === "text");
  if (!textBlock) {
    throw new Error("Claude returned no text content");
  }

  return {
    text: textBlock.text,
    stopReason: data.stop_reason,
    stopSequence: data.stop_sequence,
  };
}
