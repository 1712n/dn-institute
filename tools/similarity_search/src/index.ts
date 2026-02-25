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

// Cloudflare Workers AI bge-base-en-v1.5 supports max 100 texts per call
const EMBEDDING_BATCH_LIMIT = 100
// Max items per batch request to bound CPU time and subrequests
const MAX_BATCH_SIZE = 100
// Max text length per item to prevent abuse
const MAX_TEXT_LENGTH = 10000

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
  const data = await c.req.json<BatchRequest>()
  const { items } = data

  // Validate items array
  if (!Array.isArray(items) || items.length === 0) {
    return c.text("Invalid request: 'items' must be a non-empty array", 400)
  }

  if (items.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size ${items.length} exceeds maximum of ${MAX_BATCH_SIZE}`,
      400
    )
  }

  // Validate each item
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (typeof item.text !== "string" || typeof item.namespace !== "string") {
      return c.text(
        `Invalid item at index ${i}: 'text' and 'namespace' must be strings`,
        400
      )
    }
    if (item.text.length > MAX_TEXT_LENGTH) {
      return c.text(
        `Item at index ${i} exceeds maximum text length of ${MAX_TEXT_LENGTH}`,
        400
      )
    }
  }

  // Generate embeddings in chunks to respect CF Workers AI limits.
  // bge-base-en-v1.5 accepts up to 100 texts per call natively,
  // so we batch into chunks of EMBEDDING_BATCH_LIMIT.
  const allTexts = items.map((item) => item.text)
  const allVectors: number[][] = []

  for (let i = 0; i < allTexts.length; i += EMBEDDING_BATCH_LIMIT) {
    const chunk = allTexts.slice(i, i + EMBEDDING_BATCH_LIMIT)
    const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: chunk
    })
    allVectors.push(...modelResp.data)
  }

  // Group by namespace for efficient parallel Vectorize queries.
  // Each unique namespace requires separate queries since Vectorize
  // filters by namespace at query time.
  const namespaceGroups = new Map<
    string,
    { index: number; vector: number[] }[]
  >()
  for (let i = 0; i < items.length; i++) {
    const ns = items[i].namespace
    const group = namespaceGroups.get(ns)
    if (group) {
      group.push({ index: i, vector: allVectors[i] })
    } else {
      namespaceGroups.set(ns, [{ index: i, vector: allVectors[i] }])
    }
  }

  // Execute all Vectorize queries in parallel across all items.
  // Each query is independent and can run concurrently.
  const results: BatchResultItem[] = new Array(items.length)
  const queryPromises: Promise<void>[] = []

  for (const [namespace, groupItems] of namespaceGroups) {
    for (const { index, vector } of groupItems) {
      queryPromises.push(
        c.env.VECTORIZE_INDEX.query(vector, {
          namespace,
          topK: 1
        }).then((searchResponse) => {
          results[index] = {
            text: items[index].text,
            namespace,
            similarity_score: searchResponse.matches[0]?.score || 0
          }
        })
      )
    }
  }

  await Promise.all(queryPromises)

  return c.json({ results })
})

export default app
