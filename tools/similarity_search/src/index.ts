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
  similarity_score: number
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

// 🌰 Batch endpoint for processing multiple texts efficiently
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchRequest>()
  const { items } = data

  if (!Array.isArray(items) || items.length === 0) {
    return c.text("Invalid JSON format: 'items' must be a non-empty array", 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size exceeds maximum limit of ${MAX_BATCH_SIZE} items`,
      400
    )
  }

  // Validate all items
  for (const item of items) {
    if (typeof item.text !== "string" || typeof item.namespace !== "string") {
      return c.text("Invalid JSON format: each item must have 'text' and 'namespace' strings", 400)
    }
  }

  // 🌰 Batch embed all texts in a single AI call for efficiency
  const texts = items.map((item) => item.text)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })
  const vectors = modelResp.data

  // 🌰 Group items by namespace for efficient Vectorize queries
  const namespaceGroups = new Map<string, { index: number; vector: number[] }[]>()
  for (let i = 0; i < items.length; i++) {
    const ns = items[i].namespace
    if (!namespaceGroups.has(ns)) {
      namespaceGroups.set(ns, [])
    }
    namespaceGroups.get(ns)!.push({ index: i, vector: vectors[i] })
  }

  // Query Vectorize per namespace group in parallel
  const results: BatchResultItem[] = new Array(items.length)

  const queryPromises = Array.from(namespaceGroups.entries()).map(
    async ([namespace, groupItems]) => {
      // Query each vector within the namespace group concurrently
      const vectorQueryPromises = groupItems.map(async ({ index, vector }) => {
        const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
          namespace,
          topK: 1
        })
        const similarityScore = searchResponse.matches[0]?.score || 0
        results[index] = {
          text: items[index].text,
          namespace,
          similarity_score: similarityScore
        }
      })
      await Promise.all(vectorQueryPromises)
    }
  )

  await Promise.all(queryPromises)

  return c.json({ results })
})

export default app
