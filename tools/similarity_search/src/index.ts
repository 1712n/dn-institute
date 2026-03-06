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
  items: TextEntry[]
}

type BatchResultItem = {
  text: string
  namespace: string
  similarity_score: number | null
  error?: string
}

/** 🌰 bge-base-en-v1.5 supports up to 100 texts per embedding call */
const MAX_BATCH_SIZE = 100

/** 🌰 Guard against oversized individual texts */
const MAX_TEXT_LENGTH = 10_000

const app = new Hono<{ Bindings: Env }>()

// 🌰 Authentication middleware — shared across all endpoints
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

// 🌰 Single-message endpoint (unchanged, backward-compatible)
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

// 🌰 Batch processing endpoint
app.post("/batch", async (c) => {
  const body = await c.req.json<BatchRequest>()
  const { items } = body

  // --- Input validation 🌰 ---
  if (!Array.isArray(items) || items.length === 0) {
    return c.json({ error: "items must be a non-empty array" }, 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.json(
      { error: `Batch size exceeds maximum of ${MAX_BATCH_SIZE}` },
      400
    )
  }

  // Per-item validation with index reporting
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (typeof item?.text !== "string" || typeof item?.namespace !== "string") {
      return c.json(
        { error: `Invalid item at index ${i}: text and namespace must be strings` },
        400
      )
    }
    if (item.text.length === 0) {
      return c.json(
        { error: `Invalid item at index ${i}: text must not be empty` },
        400
      )
    }
    if (item.text.length > MAX_TEXT_LENGTH) {
      return c.json(
        { error: `Invalid item at index ${i}: text exceeds maximum length of ${MAX_TEXT_LENGTH}` },
        400
      )
    }
  }

  // --- Deduplicate texts to minimize embedding cost 🌰 ---
  const uniqueTexts: string[] = []
  const textToIndex = new Map<string, number>()
  for (const item of items) {
    if (!textToIndex.has(item.text)) {
      textToIndex.set(item.text, uniqueTexts.length)
      uniqueTexts.push(item.text)
    }
  }

  // --- Single AI.run() call for all unique texts 🌰 ---
  // bge-base-en-v1.5 natively supports batched input (up to 100 texts)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: uniqueTexts
  })

  // --- Parallel Vectorize queries with partial failure handling 🌰 ---
  const queryPromises = items.map(async (item, i): Promise<BatchResultItem> => {
    try {
      const embeddingIndex = textToIndex.get(item.text)!
      const vector = modelResp.data[embeddingIndex]
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: item.namespace,
        topK: 1
      })
      return {
        text: item.text,
        namespace: item.namespace,
        similarity_score: searchResponse.matches[0]?.score || 0
      }
    } catch (err) {
      return {
        text: item.text,
        namespace: item.namespace,
        similarity_score: null,
        error: `Query failed for item at index ${i}`
      }
    }
  })

  const results = await Promise.allSettled(queryPromises)

  // Map settled results, preserving input order 🌰
  const mappedResults: BatchResultItem[] = results.map((result, i) => {
    if (result.status === "fulfilled") {
      return result.value
    }
    return {
      text: items[i].text,
      namespace: items[i].namespace,
      similarity_score: null,
      error: `Query failed for item at index ${i}`
    }
  })

  return c.json({ results: mappedResults })
})

export default app
