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

type BatchResult = {
  text: string
  namespace: string
  similarity_score: number
}

// Maximum number of texts per Workers AI embedding call (Cloudflare limit)
const MAX_EMBEDDING_BATCH_SIZE = 100

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

// Single message similarity search (existing endpoint)
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

// Batch message similarity search
app.post("/batch", async (c) => {
  const entries = await c.req.json<TextEntry[]>()

  // Validate that the input is a non-empty array
  if (!Array.isArray(entries) || entries.length === 0) {
    return c.text("Invalid JSON format: expected a non-empty array of text entries", 400)
  }

  // Validate each entry
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i]
    if (typeof entry.text !== "string" || typeof entry.namespace !== "string") {
      return c.text(`Invalid JSON format at index ${i}: each entry must have "text" and "namespace" strings`, 400)
    }
  }

  // Collect all texts for batch embedding. Workers AI natively supports
  // embedding up to 100 texts in a single call, so we split into chunks
  // of MAX_EMBEDDING_BATCH_SIZE to leverage this native batching.
  const allTexts = entries.map((e) => e.text)
  const allVectors: number[][] = []

  for (let i = 0; i < allTexts.length; i += MAX_EMBEDDING_BATCH_SIZE) {
    const textChunk = allTexts.slice(i, i + MAX_EMBEDDING_BATCH_SIZE)
    const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: textChunk
    })
    allVectors.push(...modelResp.data)
  }

  // Query Vectorize in parallel for all vectors. Each query is independent,
  // so we use Promise.all to maximize throughput.
  const queryPromises = allVectors.map((vector, idx) =>
    c.env.VECTORIZE_INDEX.query(vector, {
      namespace: entries[idx].namespace,
      topK: 1
    })
  )
  const queryResults = await Promise.all(queryPromises)

  // Build the response, preserving original request order
  const results: BatchResult[] = entries.map((entry, idx) => ({
    text: entry.text,
    namespace: entry.namespace,
    similarity_score: queryResults[idx].matches[0]?.score || 0
  }))

  return c.json(results)
})

export default app
