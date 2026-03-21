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

// 🌰 Maximum number of entries per batch request, balancing Cloudflare Workers
// CPU/memory limits with throughput. The bge-base-en-v1.5 model supports batched
// input natively, so we leverage that for efficient embedding generation.
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

// 🌰 Single text similarity search (original endpoint)
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

// 🌰 Batch text similarity search endpoint
// Accepts an array of text entries and returns similarity scores for each.
// Leverages Cloudflare Workers AI native batch embedding support to generate
// all vectors in a single model call, then queries Vectorize in parallel.
app.post("/batch", async (c) => {
  const data = await c.req.json<{ entries: TextEntry[] }>()
  const { entries } = data

  if (!Array.isArray(entries)) {
    return c.text("Invalid JSON format: 'entries' must be an array", 400)
  }

  if (entries.length === 0) {
    return c.json({ results: [] })
  }

  if (entries.length > MAX_BATCH_SIZE) {
    return c.text(
      `Batch size exceeds maximum of ${MAX_BATCH_SIZE} entries`,
      400
    )
  }

  // 🌰 Validate all entries before processing
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i]
    if (typeof entry.text !== "string" || typeof entry.namespace !== "string") {
      return c.text(`Invalid JSON format at entry index ${i}`, 400)
    }
  }

  // 🌰 Single batched AI call — the bge-base-en-v1.5 model natively supports
  // multiple texts, so we get all embeddings in one request instead of N calls.
  const texts = entries.map((e) => e.text)
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })

  // 🌰 Parallel Vectorize queries — each vector is queried concurrently to
  // minimize wall-clock time. Cloudflare Vectorize handles concurrent reads
  // efficiently without additional cost per query.
  const results = await Promise.all(
    entries.map(async (entry, i) => {
      const vector = modelResp.data[i]
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: entry.namespace,
        topK: 1
      })
      const similarityScore = searchResponse.matches[0]?.score || 0
      return { text: entry.text, namespace: entry.namespace, similarity_score: similarityScore }
    })
  )

  return c.json({ results })
})

export default app
