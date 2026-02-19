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

/** Maximum items per batch request — keeps us within Workers CPU limits */
const MAX_BATCH_SIZE = 100

const app = new Hono<{ Bindings: Env }>()

// 🌰 Authentication middleware
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

// 🌰 Single text similarity search
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

// 🌰 Batch similarity search
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchRequest>()
  const { items } = data

  // Validate top-level structure
  if (!Array.isArray(items) || items.length === 0) {
    return c.text("Invalid JSON format: 'items' must be a non-empty array", 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size exceeds maximum of ${MAX_BATCH_SIZE} items`,
      400
    )
  }

  // Validate each item
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (typeof item.text !== "string" || typeof item.namespace !== "string") {
      return c.text(
        `Invalid JSON format: item at index ${i} must have 'text' and 'namespace' as strings`,
        400
      )
    }
  }

  // Single AI call for all texts — bge-base-en-v1.5 supports native batching
  const allTexts = items.map((item) => item.text)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: allTexts
  })
  const vectors = modelResp.data

  // Group items by namespace for efficient Vectorize queries
  const namespaceGroups = new Map<number[], { index: number; namespace: string }>()
  const indexedVectors: { index: number; vector: number[]; namespace: string }[] = []
  for (let i = 0; i < items.length; i++) {
    indexedVectors.push({
      index: i,
      vector: vectors[i],
      namespace: items[i].namespace
    })
  }

  // Query Vectorize in parallel, grouped by namespace
  const byNamespace = new Map<string, { index: number; vector: number[] }[]>()
  for (const iv of indexedVectors) {
    const group = byNamespace.get(iv.namespace) || []
    group.push({ index: iv.index, vector: iv.vector })
    byNamespace.set(iv.namespace, group)
  }

  const results: BatchResultItem[] = new Array(items.length)

  // Parallel queries per namespace
  const queryPromises = Array.from(byNamespace.entries()).map(
    async ([namespace, entries]) => {
      // Query each vector in this namespace in parallel
      const entryPromises = entries.map(async (entry) => {
        const searchResponse = await c.env.VECTORIZE_INDEX.query(
          entry.vector,
          { namespace, topK: 1 }
        )
        const score = searchResponse.matches[0]?.score || 0
        results[entry.index] = {
          text: items[entry.index].text,
          namespace,
          similarity_score: score
        }
      })
      await Promise.all(entryPromises)
    }
  )

  await Promise.all(queryPromises)

  return c.json({ results })
})

export default app
