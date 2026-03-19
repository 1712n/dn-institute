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
  id?: string
}

type BatchRequest = {
  items: BatchEntry[]
}

type BatchResultItem = {
  id?: string
  text: string
  namespace: string
  similarity_score: number
}

const MAX_BATCH_SIZE = 100
const EMBEDDING_CHUNK_SIZE = 20

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

// Single text similarity (backward compatible)
app.post("/", async (c) => {
  const data = await c.req.json<TextEntry>()
  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const score = await computeSimilarity(c.env, text, namespace)
  return c.json({ similarity_score: score })
})

// Batch processing endpoint
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchRequest>()

  if (!Array.isArray(data.items) || data.items.length === 0) {
    return c.text("Invalid batch format: 'items' must be a non-empty array", 400)
  }

  if (data.items.length > MAX_BATCH_SIZE) {
    return c.text(`Batch size exceeds maximum of ${MAX_BATCH_SIZE}`, 400)
  }

  for (const item of data.items) {
    if (typeof item.text !== "string" || typeof item.namespace !== "string") {
      return c.text("Each item must have 'text' and 'namespace' string fields", 400)
    }
  }

  const results = await processBatch(c.env, data.items)
  return c.json({ results })
})

async function computeSimilarity(
  env: Env,
  text: string,
  namespace: string
): Promise<number> {
  const modelResp = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: [text]
  })
  const vector = modelResp.data[0]
  const searchResponse = await env.VECTORIZE_INDEX.query(vector, {
    namespace,
    topK: 1
  })
  return searchResponse.matches[0]?.score || 0
}

async function processBatch(
  env: Env,
  items: BatchEntry[]
): Promise<BatchResultItem[]> {
  // Group items by namespace to optimize vectorize queries
  const byNamespace = new Map<string, { index: number; item: BatchEntry }[]>()
  for (let i = 0; i < items.length; i++) {
    const ns = items[i].namespace
    if (!byNamespace.has(ns)) byNamespace.set(ns, [])
    byNamespace.get(ns)!.push({ index: i, item: items[i] })
  }

  const results: BatchResultItem[] = new Array(items.length)

  // Process each namespace group
  const namespacePromises = Array.from(byNamespace.entries()).map(
    async ([namespace, entries]) => {
      // Chunk embeddings to stay within AI model limits
      for (let i = 0; i < entries.length; i += EMBEDDING_CHUNK_SIZE) {
        const chunk = entries.slice(i, i + EMBEDDING_CHUNK_SIZE)
        const texts = chunk.map((e) => e.item.text)

        // Batch embedding call — single API call for multiple texts
        const modelResp = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
          text: texts
        })

        // Query vectorize for each embedding in the chunk
        const queryPromises = chunk.map(async (entry, j) => {
          const vector = modelResp.data[j]
          const searchResponse = await env.VECTORIZE_INDEX.query(vector, {
            namespace,
            topK: 1
          })
          const score = searchResponse.matches[0]?.score || 0

          results[entry.index] = {
            id: entry.item.id,
            text: entry.item.text,
            namespace: entry.item.namespace,
            similarity_score: score
          }
        })

        await Promise.all(queryPromises)
      }
    }
  )

  await Promise.all(namespacePromises)
  return results
}

export default app
