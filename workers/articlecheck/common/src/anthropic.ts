export type AnthropicMessage = { role: "user" | "assistant"; content: string };

export async function anthropicCreateMessage(opts: {
  apiKey: string;
  model: string;
  system: string;
  messages: AnthropicMessage[];
  maxTokens: number;
  temperature: number;
  stopSequences?: string[];
  timeoutMs?: number;
}): Promise<string> {
  const ctrl = new AbortController();
  const timeout = setTimeout(() => ctrl.abort(), opts.timeoutMs ?? 60_000);
  try {
    const resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      signal: ctrl.signal,
      headers: {
        "content-type": "application/json",
        "x-api-key": opts.apiKey,
        // Keep the stable version header for broad compatibility.
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: opts.model,
        max_tokens: opts.maxTokens,
        temperature: opts.temperature,
        system: opts.system,
        stop_sequences: opts.stopSequences,
        messages: opts.messages.map((m) => ({
          role: m.role,
          content: [{ type: "text", text: m.content }]
        }))
      })
    });
    const text = await resp.text();
    if (!resp.ok) {
      throw new Error(`anthropic_error status=${resp.status} body=${text.slice(0, 1200)}`);
    }
    const data = JSON.parse(text) as { content: Array<{ type: string; text: string }> };
    const first = data?.content?.find((c) => c?.type === "text");
    if (!first?.text) throw new Error("anthropic_missing_text_content");
    return first.text;
  } finally {
    clearTimeout(timeout);
  }
}

