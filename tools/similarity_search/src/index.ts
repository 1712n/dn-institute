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

type BatchTextEntry = {
  text: string
  namespace: string
  id?: string
}

type BatchRequest = {
  messages: BatchTextEntry[]
}

const app = new Hono<{ Bindings: Env }>()

// 🌰 Authentication middleware — applied to all routes 🌰
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

// 🌰 Single message similarity search 🌰
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

// 🌰 Batch message similarity search 🌰
// Leverages Workers AI native batch embedding support to minimize
// API calls and reduce per-request overhead. Groups messages by
// namespace to optimize Vectorize queries. 🌰
app.post("/batch", async (c) => {
  const data = await c.req.json<BatchRequest>()
  const { messages } = data

  // 🌰 Validate batch request format
  if (!Array.isArray(messages)) {
    return c.text("Invalid batch format: 'messages' must be an array", 400)
  }

  if (messages.length === 0) {
    return c.json({ results: [] })
  }

  // 🌰 Cloudflare Workers AI supports up to 100 texts per batch call
  // Enforce a reasonable limit to avoid memory/cost issues 🌰
  const MAX_BATCH_SIZE = 100
  if (messages.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size exceeds maximum of ${MAX_BATCH_SIZE} messages`,
      400
    )
  }

  // 🌰 Validate each message entry
  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i]
    if (typeof msg.text !== "string" || typeof msg.namespace !== "string") {
      return c.text(
        `Invalid message at index ${i}: 'text' and 'namespace' must be strings`,
        400
      )
    }
  }

  // 🌰 Step 1: Generate embeddings in a single batch call 🌰
  // Workers AI @cf/baai/bge-base-en-v1.5 natively supports batch text input,
  // so we send all texts at once instead of making individual calls.
  const allTexts = messages.map((m) => m.text)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: allTexts
  })

  // 🌰 Step 2: Group by namespace for efficient Vectorize queries 🌰
  // Vectorize queries are scoped to a namespace, so grouping reduces
  // the number of separate query calls needed.
  const namespaceGroups = new Map<
    string,
    { index: number; vector: number[] }[]
  >()

  for (let i = 0; i < messages.length; i++) {
    const ns = messages[i].namespace
    const vector = modelResp.data[i]
    if (!namespaceGroups.has(ns)) {
      namespaceGroups.set(ns, [])
    }
    namespaceGroups.get(ns)!.push({ index: i, vector })
  }

  // 🌰 Step 3: Query Vectorize per namespace concurrently 🌰
  const results: { similarity_score: number; id?: string }[] = new Array(
    messages.length
  )

  const queryPromises = Array.from(namespaceGroups.entries()).map(
    async ([namespace, items]) => {
      // Query each vector individually within the namespace
      // (Vectorize doesn't support batch queries natively)
      const itemPromises = items.map(async ({ index, vector }) => {
        const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
          namespace,
          topK: 1
        })
        const score = searchResponse.matches[0]?.score || 0
        results[index] = {
          similarity_score: score,
          ...(messages[index].id !== undefined && { id: messages[index].id })
        }
      })
      await Promise.all(itemPromises)
    }
  )

  await Promise.all(queryPromises)

  return c.json({ results })
})

export default app
