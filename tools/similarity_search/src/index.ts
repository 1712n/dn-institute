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

/**
 * Workers AI embedding models accept up to 100 texts per call.
 * Each Vectorize query counts as a subrequest; Workers have a limit of 50
 * concurrent subrequests on the free plan (1000 on paid). We cap batch size
 * conservatively to stay well within free-tier limits while leaving headroom
 * for the AI call itself.
 */
const MAX_BATCH_SIZE = 100

const app = new Hono<{ Bindings: Env }>()

// Auth middleware
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

// Single message endpoint (unchanged behavior)
app.post("/", async (c) => {
  const data = await c.req.json<TextEntry>()
  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: [text]
  })
  const vector = modelResp.data[0]
  const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
    namespace,
    topK: 1
  })
  const similarityScore = searchResponse.matches[0]?.score || 0

  return c.json({ similarity_score: similarityScore })
})

// Batch message endpoint
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchRequest>()
  const { messages } = data

  if (!Array.isArray(messages) || messages.length === 0) {
    return c.text("Invalid request: expected non-empty 'messages' array", 400)
  }

  if (messages.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size ${messages.length} exceeds maximum of ${MAX_BATCH_SIZE}`,
      400
    )
  }

  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i]
    if (
      typeof msg.text !== "string" ||
      typeof msg.namespace !== "string" ||
      msg.text.trim().length === 0
    ) {
      return c.text(
        `Invalid message at index ${i}: 'text' and 'namespace' must be non-empty strings`,
        400
      )
    }
  }

  // Deduplicate texts to avoid redundant embedding computations.
  // Workers AI charges per token processed, so embedding each unique text
  // only once reduces cost when a batch contains repeated messages.
  const uniqueTexts = [...new Set(messages.map((m) => m.text))]
  const textToIndex = new Map<string, number>()
  uniqueTexts.forEach((t, i) => textToIndex.set(t, i))

  // Single AI call for all unique texts — the embedding model natively
  // supports batched input, so this is one subrequest regardless of count.
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: uniqueTexts
  })
  const vectors = modelResp.data

  // Parallel Vectorize queries — each query is independent and can run
  // concurrently. We map each original message to its deduplicated vector.
  const scores = await Promise.all(
    messages.map((msg) => {
      const vecIdx = textToIndex.get(msg.text)!
      return c.env.VECTORIZE_INDEX.query(vectors[vecIdx], {
        namespace: msg.namespace,
        topK: 1
      }).then((res) => res.matches[0]?.score || 0)
    })
  )

  return c.json({
    results: scores.map((score) => ({ similarity_score: score }))
  })
})

export default app
