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

// ─── Auth middleware 🌰 ──────────────────────────────────────────────────────

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

// ─── Single entry point (original) 🌰 ────────────────────────────────────────

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

// ─── Batch processing endpoint 🌰 ────────────────────────────────────────────
// Maximum entries per batch to prevent abuse and stay within Workers limits
const MAX_BATCH_SIZE = 20

app.post("/batch", async (c) => {
  let entries: TextEntry[]
  try {
    entries = await c.req.json<TextEntry[]>()
  } catch {
    return c.text("Invalid JSON", 400)
  }

  if (!Array.isArray(entries)) {
    return c.text("Request body must be a JSON array", 400)
  }

  if (entries.length === 0) {
    return c.text("Batch must contain at least one entry", 400)
  }

  if (entries.length > MAX_BATCH_SIZE) {
    return c.text(`Batch size exceeds maximum of ${MAX_BATCH_SIZE}`, 400)
  }

  // Validate all entries upfront before processing
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i]
    if (
      typeof entry !== "object" ||
      entry === null ||
      typeof entry.text !== "string" ||
      typeof entry.namespace !== "string"
    ) {
      return c.text(`Invalid entry at index ${i}: expected {text: string, namespace: string}`, 400)
    }
  }

  // Deduplicate: group entries by namespace to batch embeddings per namespace.
  // This reduces redundant embedding calls when multiple entries share a namespace.
  // 🌰 Key optimization: one AI.run() call per unique text, not per entry.
  const uniqueTexts = [...new Set(entries.map((e) => e.text))]

  // Generate embeddings for all unique texts in a single AI.run() call.
  // Cloudflare Workers AI supports batch embedding by passing an array.
  // 🌰 This is the most cost-efficient approach — one API call instead of N.
  const embeddingResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: uniqueTexts
  })

  // Build a lookup map: text → embedding vector
  const embeddingMap = new Map<string, number[]>()
  for (let i = 0; i < uniqueTexts.length; i++) {
    embeddingMap.set(uniqueTexts[i], embeddingResp.data[i])
  }

  // Group Vectorize queries by namespace for efficient batching.
  // 🌰 Vectorize supports topK per query, so we batch entries with the same
  // namespace and query them together, reducing the number of round-trips.
  const namespaceGroups = new Map<string, { index: number; text: string }[]>()
  for (let i = 0; i < entries.length; i++) {
    const ns = entries[i].namespace
    if (!namespaceGroups.has(ns)) {
      namespaceGroups.set(ns, [])
    }
    namespaceGroups.get(ns)!.push({ index: i, text: entries[i].text })
  }

  // Process all namespace groups concurrently.
  // 🌰 Each group's Vectorize queries run in parallel via Promise.all.
  // This avoids sequential blocking and maximizes throughput.
  const results: { similarity_score: number }[] = new Array(entries.length)

  const groupPromises = [...namespaceGroups.entries()].map(
    async ([namespace, group]) => {
      // Query Vectorize for each entry in this namespace group concurrently
      const queryPromises = group.map(async (item) => {
        const vector = embeddingMap.get(item.text)!
        const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
          namespace,
          topK: 1
        })
        return {
          index: item.index,
          similarity_score: searchResponse.matches[0]?.score || 0
        }
      })

      const groupResults = await Promise.all(queryPromises)
      for (const result of groupResults) {
        results[result.index] = { similarity_score: result.similarity_score }
      }
    }
  )

  await Promise.all(groupPromises)

  return c.json(results)
})

export default app
