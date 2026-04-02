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

type BatchEntry = {
  text: string
  namespace: string
}

type BatchResultItem = {
  index: number
  similarity_score: number
  error?: string
}

const app = new Hono<{ Bindings: Env }>()

// Rate limiting configuration
const MAX_BATCH_SIZE = 50

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

app.post("/batch", async (c) => {
  const data = await c.req.json<{ entries: BatchEntry[] }>()
  const { entries } = data

  if (!Array.isArray(entries)) {
    return c.text("Invalid JSON format: entries must be an array", 400)
  }

  if (entries.length === 0) {
    return c.json({ results: [], message: "No entries provided" })
  }

  if (entries.length > MAX_BATCH_SIZE) {
    return c.text("Batch size exceeds maximum of " + MAX_BATCH_SIZE, 400)
  }

  // Validate each entry
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i]
    if (typeof entry.text !== "string" || typeof entry.namespace !== "string") {
      return c.text("Invalid JSON format at index " + i + ": text and namespace must be strings", 400)
    }
  }

  // Generate embeddings for all texts in parallel
  const texts = entries.map(e => e.text)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })

  const vectors = modelResp.data

  // Process each entry and query Vectorize
  const results: BatchResultItem[] = []
  
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i]
    const vector = vectors[i]
    
    try {
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: entry.namespace,
        topK: 1
      })
      
      const similarityScore = searchResponse.matches[0]?.score || 0
      results.push({
        index: i,
        similarity_score: similarityScore
      })
    } catch (error) {
      // Handle partial failure - include error but continue processing
      const errorMessage = error instanceof Error ? error.message : "Unknown error"
      results.push({
        index: i,
        similarity_score: 0,
        error: errorMessage
      })
    }
  }

  return c.json({ results })
})

export default app
