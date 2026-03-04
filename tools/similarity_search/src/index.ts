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

type BatchTextEntry = {
  texts: string[]
  namespace: string
}

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

// Single text processing (original endpoint)
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

// Batch text processing (new endpoint)
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchTextEntry>()
  const { texts, namespace } = data

  if (!Array.isArray(texts) || texts.length === 0) {
    return c.text("Invalid JSON format: texts must be a non-empty array", 400)
  }

  // Validate all texts are strings
  for (const text of texts) {
    if (typeof text !== "string") {
      return c.text("Invalid JSON format: all texts must be strings", 400)
    }
  }

  // Run embedding model for all texts in batch
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })

  if (!modelResp.data || modelResp.data.length !== texts.length) {
    return c.text("Embedding model failed to process all texts", 500)
  }

  // Query vectorize for all vectors in batch
  const queries = modelResp.data.map((vector) => ({
    vector,
    options: {
      namespace,
      topK: 1
    }
  }))

  // Use Promise.all for parallel queries (native Cloudflare functionality)
  const searchResponses = await Promise.all(
    queries.map((query) => c.env.VECTORIZE_INDEX.query(query.vector, query.options))
  )

  // Return batch results
  const results = searchResponses.map((response) => ({
    similarity_score: response.matches[0]?.score || 0
  }))

  return c.json({ results })
})

export default app
