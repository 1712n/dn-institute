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
  const data = await c.req.json<{ items: TextEntry[] }>()
  const { items } = data

  if (!Array.isArray(items) || items.length === 0) {
    return c.text("Invalid batch format: 'items' must be a non-empty array", 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size limit exceeded: received ${items.length}, maximum is ${MAX_BATCH_SIZE}`,
      400
    )
  }

  // Validate each item before processing
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (typeof item.text !== "string" || typeof item.namespace !== "string") {
      return c.text(
        `Invalid item at index ${i}: 'text' and 'namespace' must be strings`,
        400
      )
    }
  }

  // Batch embedding: leverage Workers AI native batch support by sending
  // all texts in a single inference call. This avoids per-item API overhead
  // and is significantly more efficient than individual calls.
  const allTexts = items.map((item) => item.text)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: allTexts
  })

  // Parallel Vectorize queries: Vectorize does not support batch query
  // natively, so we issue concurrent individual queries. Since each query
  // targets potentially different namespaces, this is the most efficient
  // approach without adding custom infrastructure.
  const results = await Promise.all(
    items.map(async (item, index) => {
      const vector = modelResp.data[index]
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: item.namespace,
        topK: 1
      })
      return {
        text: item.text,
        namespace: item.namespace,
        similarity_score: searchResponse.matches[0]?.score || 0
      }
    })
  )

  return c.json({ results })
})

export default app
