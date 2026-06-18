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
  error?: string
}

const MAX_BATCH_SIZE = 100
const MAX_TEXT_LENGTH = 8192

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
  let data: { items?: unknown }
  try {
    data = await c.req.json()
  } catch {
    return c.json({ error: "Invalid JSON body" }, 400)
  }

  const { items } = data

  if (!Array.isArray(items)) {
    return c.json({ error: "items must be an array" }, 400)
  }

  if (items.length === 0) {
    return c.json({ error: "items must not be empty" }, 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.json(
      { error: `Batch size exceeds maximum of ${MAX_BATCH_SIZE}` },
      400
    )
  }

  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (
      typeof item.text !== "string" ||
      typeof item.namespace !== "string"
    ) {
      return c.json(
        { error: `Invalid item at index ${i}: text and namespace must be strings` },
        400
      )
    }
    if (item.text.length > MAX_TEXT_LENGTH) {
      return c.json(
        { error: `Item at index ${i} exceeds maximum text length of ${MAX_TEXT_LENGTH}` },
        400
      )
    }
  }

  // Deduplicate texts for embedding to minimize AI calls
  const uniqueTexts = [...new Set(items.map((item) => item.text))]

  // Embed all unique texts in a single AI call (native batch, max 100)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: uniqueTexts
  })

  if (!modelResp.data || modelResp.data.length !== uniqueTexts.length) {
    return c.json({ error: "Embedding service returned unexpected response" }, 502)
  }

  const embeddingMap = new Map<string, number[]>()
  for (let i = 0; i < uniqueTexts.length; i++) {
    embeddingMap.set(uniqueTexts[i], modelResp.data[i])
  }

  // Query vectorize for each item, using Promise.allSettled for partial failure tolerance
  const queryResults = await Promise.allSettled(
    items.map(async (item) => {
      const vector = embeddingMap.get(item.text)
      if (!vector) {
        throw new Error("Missing embedding for text")
      }
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: item.namespace,
        topK: 1
      })
      return searchResponse.matches[0]?.score || 0
    })
  )

  const results: BatchResult[] = items.map((item, i) => {
    const result = queryResults[i]
    if (result.status === "fulfilled") {
      return {
        text: item.text,
        namespace: item.namespace,
        similarity_score: result.value
      }
    }
    return {
      text: item.text,
      namespace: item.namespace,
      similarity_score: 0,
      error: "Query failed"
    }
  })

  return c.json({ results })
})

export default app
