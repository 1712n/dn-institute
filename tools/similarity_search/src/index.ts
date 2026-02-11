import { Hono } from "hono"

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
}

type TextEntry = {
  text: string
  namespace: string
}

type BatchRequest = {
  messages: TextEntry[]
}

// Cloudflare Workers subrequest limit is 50. Each Vectorize query is 1 subrequest,
// plus 1 for the AI embedding call, leaving room for 48 batch items.
const MAX_BATCH_SIZE = 48

const app = new Hono<{ Bindings: Env }>()

app.use("*", async (c, next) => {
  const apiKey = c.env.API_KEY_TOKEN_CHECK
  if (!apiKey) {
    return c.text("API key not found", 400)
  }

  const apiKeyHeader = c.req.header("X-API-Key")
  if (!apiKeyHeader || apiKeyHeader !== c.env.API_KEY_TOKEN_CHECK) {
    return c.text("Unauthorized", 401)
  }

  return next()
})

async function embedTexts(ai: Ai, texts: string[]): Promise<number[][]> {
  const modelResp = await ai.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })
  return modelResp.data
}

async function querySimilarity(
  index: VectorizeIndex,
  vector: number[],
  namespace: string
): Promise<number> {
  const searchResponse = await index.query(vector, {
    namespace,
    topK: 1
  })
  return searchResponse.matches[0]?.score || 0
}

app.post("/", async (c) => {
  const data = await c.req.json<TextEntry>()
  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const vectors = await embedTexts(c.env.AI, [text])
  const similarityScore = await querySimilarity(c.env.VECTORIZE_INDEX, vectors[0], namespace)

  return c.json({ similarity_score: similarityScore })
})

app.post("/batch", async (c) => {
  const data = await c.req.json<BatchRequest>()
  const { messages } = data

  if (!Array.isArray(messages) || messages.length === 0) {
    return c.text("Invalid JSON format: expected non-empty 'messages' array", 400)
  }

  if (messages.length > MAX_BATCH_SIZE) {
    return c.text(`Batch size exceeds maximum of ${MAX_BATCH_SIZE}`, 400)
  }

  for (const msg of messages) {
    if (typeof msg.text !== "string" || typeof msg.namespace !== "string") {
      return c.text("Invalid JSON format: each message must have 'text' and 'namespace' strings", 400)
    }
  }

  // Single AI call for all texts — native batch support in the embedding model
  const texts = messages.map((m) => m.text)
  const vectors = await embedTexts(c.env.AI, texts)

  // Parallel Vectorize queries for each vector
  const scores = await Promise.all(
    vectors.map((vector, i) =>
      querySimilarity(c.env.VECTORIZE_INDEX, vector, messages[i].namespace)
    )
  )

  const results = scores.map((score) => ({ similarity_score: score }))

  return c.json({ results })
})

export default app
