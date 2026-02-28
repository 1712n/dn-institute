/**
 * 🌰 Claude Messages API client for the fact-checking pipeline
 */

import type { ClaudeResponse } from "./types"

const CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
const CLAUDE_API_VERSION = "2023-06-01"

/** Model for fact-checking (accuracy-critical) */
export const SEARCH_MODEL = "claude-3-opus-20240229"

/** Model for summarization (cost-efficient) */
export const SUMMARIZE_MODEL = "claude-3-haiku-20240307"

/**
 * Call Claude Messages API.
 */
export async function callClaude(params: {
  apiKey: string
  model: string
  system: string
  messages: Array<{ role: string; content: Array<{ type: string; text: string }> }>
  maxTokens: number
  temperature: number
  stopSequences?: string[]
}): Promise<ClaudeResponse> {
  const body: Record<string, unknown> = {
    model: params.model,
    max_tokens: params.maxTokens,
    temperature: params.temperature,
    system: params.system,
    messages: params.messages,
  }

  if (params.stopSequences?.length) {
    body.stop_sequences = params.stopSequences
  }

  const response = await fetch(CLAUDE_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": params.apiKey,
      "anthropic-version": CLAUDE_API_VERSION,
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`Claude API error: ${response.status} ${text}`)
  }

  return response.json() as Promise<ClaudeResponse>
}
