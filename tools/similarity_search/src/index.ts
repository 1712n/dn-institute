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

// 🌰 Batch entry for processing multiple texts in one request
type BatchTextEntry = {
  texts: string[]
  namespace: string
}

// Sync embedding output shape for @cf/baai/bge-base-en-v1.5
type EmbeddingOutput = {
  data: number[][]
}

// Maximum texts per batch to stay within CF Workers AI limits 🌰
const MAX_BATCH_SIZE = 100

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

app.post("/", async (c) => {
  const data = await c.req.json<TextEntry>()
  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const modelResp = (await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: [text]
  })) as unknown as EmbeddingOutput
  const vector = modelResp.data[0]
  const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
    namespace,
    topK: 1
  })
  const similarityScore = searchResponse.matches[0]?.score || 0

  return c.json({ similarity_score: similarityScore })
})

// 🌰 Batch endpoint: generates embeddings for all texts in one AI call,
// then queries Vectorize in parallel — no sequential bottlenecks.
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchTextEntry>()
  const { texts, namespace } = data

  if (!Array.isArray(texts) || texts.length === 0 || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  if (!texts.every((t) => typeof t === "string")) {
    return c.text("Invalid JSON format: all texts must be strings", 400)
  }

  if (texts.length > MAX_BATCH_SIZE) {
    return c.text(`Batch size exceeds maximum of ${MAX_BATCH_SIZE}`, 400)
  }

  // 🌰 Single AI call for all embeddings — CF Workers AI handles batching natively
  const modelResp = (await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })) as unknown as EmbeddingOutput

  // 🌰 Fan out Vectorize queries in parallel — no sequential bottleneck
  const searchResults = await Promise.all(
    modelResp.data.map((vector: number[]) =>
      c.env.VECTORIZE_INDEX.query(vector, {
        namespace,
        topK: 1
      })
    )
  )

  const results = searchResults.map((searchResponse: VectorizeMatches) => ({
    similarity_score: searchResponse.matches[0]?.score || 0,
    metadata: searchResponse.matches[0]?.metadata || null
  }))

  return c.json({ results })
})

export default app
