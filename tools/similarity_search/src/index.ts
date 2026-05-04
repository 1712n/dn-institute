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

// Maximum items per batch request. Workers AI embeds one text at a time via
// bge-base-en-v1.5, so we cap the batch to avoid hitting the 30-second CPU
// time limit on Workers. 50 items × ~200ms each ≈ 10s, leaving headroom.
const MAX_BATCH_SIZE = 50

type BatchEntry = TextEntry & { id?: string }
type BatchResult = {
  id?: string
  similarity_score: number
}
type BatchErrorResult = {
  id?: string
  error: string
}

app.post("/batch", async (c) => {
  const body = await c.req.json<{ items: BatchEntry[] }>()
  const { items } = body

  if (!Array.isArray(items) || items.length === 0) {
    return c.text("Invalid JSON format: 'items' must be a non-empty array", 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch too large: maximum ${MAX_BATCH_SIZE} items per request, got ${items.length}`,
      400
    )
  }

  // Validate every entry upfront before doing any AI work
  for (let i = 0; i < items.length; i++) {
    const entry = items[i]
    if (typeof entry.text !== "string" || typeof entry.namespace !== "string") {
      return c.text(
        `Invalid item at index ${i}: 'text' and 'namespace' must be strings`,
        400
      )
    }
  }

  // Process items concurrently with allSettled so one failure doesn't abort
  // the entire batch. Each item embeds independently because the bge model
  // accepts a text array but Vectorize queries are per-namespace.
  const results = await Promise.allSettled(
    items.map(async (entry): Promise<BatchResult> => {
      const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
        text: [entry.text],
      })
      const vector = modelResp.data[0]
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: entry.namespace,
        topK: 1,
      })
      const similarityScore = searchResponse.matches[0]?.score || 0
      return {
        ...(entry.id !== undefined && { id: entry.id }),
        similarity_score: similarityScore,
      }
    })
  )

  const response: { results: (BatchResult | BatchErrorResult)[] } = {
    results: results.map((r, i) => {
      if (r.status === "fulfilled") {
        return r.value
      }
      return {
        ...(items[i].id !== undefined && { id: items[i].id }),
        error: r.reason instanceof Error ? r.reason.message : String(r.reason),
      }
    }),
  }

  return c.json(response)
})

export default app
