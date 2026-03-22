import { Hono } from "hono"

// 🌰 Similarity Search API — single + batch endpoints

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
  items: TextEntry[]
}

type BatchResultItem = {
  text: string
  namespace: string
  similarity_score: number | null
  error?: string
}

/** 🌰 Maximum batch size — aligned with bge-base-en-v1.5 input limit */
const MAX_BATCH_SIZE = 100

const app = new Hono<{ Bindings: Env }>()

// 🌰 Auth middleware — shared by all endpoints
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

// 🌰 Single-text endpoint (unchanged)
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

// 🌰 Batch endpoint — process multiple texts in a single request
app.post("/batch", async (c) => {
  const body = await c.req.json<BatchRequest>()

  // 🌰 Validate top-level structure
  if (!body.items || !Array.isArray(body.items) || body.items.length === 0) {
    return c.json({ error: "items must be a non-empty array" }, 400)
  }

  if (body.items.length > MAX_BATCH_SIZE) {
    return c.json(
      { error: `Batch size exceeds maximum of ${MAX_BATCH_SIZE}` },
      400
    )
  }

  // 🌰 Validate each item and collect errors early
  for (let i = 0; i < body.items.length; i++) {
    const item = body.items[i]
    if (typeof item.text !== "string" || item.text.trim().length === 0) {
      return c.json(
        { error: `Invalid item at index ${i}: text must be a non-empty string` },
        400
      )
    }
    if (typeof item.namespace !== "string" || item.namespace.trim().length === 0) {
      return c.json(
        { error: `Invalid item at index ${i}: namespace must be a non-empty string` },
        400
      )
    }
  }

  // 🌰 Deduplicate texts to minimize embedding compute cost
  // Multiple items may share the same text but differ in namespace
  const uniqueTexts = [...new Set(body.items.map((item) => item.text))]
  const textToIndex = new Map<string, number>()
  uniqueTexts.forEach((text, idx) => textToIndex.set(text, idx))

  // 🌰 Single AI.run() call — bge-base-en-v1.5 natively supports batch input
  // This is the primary cost optimization: 1 inference call instead of N
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: uniqueTexts
  })
  const embeddings = modelResp.data

  // 🌰 Parallel Vectorize queries via Promise.allSettled for resilience
  // A single failed query won't abort the entire batch
  const queryPromises = body.items.map((item) => {
    const embeddingIdx = textToIndex.get(item.text)!
    const vector = embeddings[embeddingIdx]
    return c.env.VECTORIZE_INDEX.query(vector, {
      namespace: item.namespace,
      topK: 1
    })
  })

  const settled = await Promise.allSettled(queryPromises)

  // 🌰 Map results back, preserving original item order
  const results: BatchResultItem[] = body.items.map((item, i) => {
    const outcome = settled[i]
    if (outcome.status === "fulfilled") {
      return {
        text: item.text,
        namespace: item.namespace,
        similarity_score: outcome.value.matches[0]?.score ?? 0
      }
    }
    return {
      text: item.text,
      namespace: item.namespace,
      similarity_score: null,
      error: "Vectorize query failed"
    }
  })

  return c.json({ results })
})

export default app
