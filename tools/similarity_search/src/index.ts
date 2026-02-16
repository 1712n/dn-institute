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

const AI_MODEL = "@cf/baai/bge-base-en-v1.5"
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

async function embedTexts(ai: Ai, texts: string[]): Promise<number[][]> {
  const response = await ai.run(AI_MODEL, { text: texts })
  return response.data
}

async function querySimilarity(
  index: VectorizeIndex,
  vector: number[],
  namespace: string
): Promise<number> {
  const response = await index.query(vector, { namespace, topK: 1 })
  return response.matches[0]?.score || 0
}

app.post("/", async (c) => {
  const data = await c.req.json<TextEntry>()
  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const [vector] = await embedTexts(c.env.AI, [text])
  const similarityScore = await querySimilarity(c.env.VECTORIZE_INDEX, vector, namespace)

  return c.json({ similarity_score: similarityScore })
})

app.post("/batch", async (c) => {
  const data = await c.req.json<{ messages: TextEntry[] }>()

  if (!Array.isArray(data.messages)) {
    return c.json({ error: "messages must be an array" }, 400)
  }
  if (data.messages.length === 0) {
    return c.json({ error: "messages array must not be empty" }, 400)
  }
  if (data.messages.length > MAX_BATCH_SIZE) {
    return c.json({ error: `batch size exceeds maximum of ${MAX_BATCH_SIZE}` }, 400)
  }

  for (const [i, entry] of data.messages.entries()) {
    if (typeof entry.text !== "string" || typeof entry.namespace !== "string") {
      return c.json({ error: `invalid format at index ${i}: text and namespace must be strings` }, 400)
    }
  }

  // Deduplicate texts for embedding — each unique text is embedded only once
  const uniqueTexts = [...new Set(data.messages.map((m) => m.text))]
  const embeddings = await embedTexts(c.env.AI, uniqueTexts)
  const embeddingMap = new Map<string, number[]>()
  uniqueTexts.forEach((text, i) => embeddingMap.set(text, embeddings[i]))

  // Deduplicate (text, namespace) pairs for Vectorize queries
  const queryKey = (text: string, namespace: string) => `${text}\0${namespace}`
  const uniqueQueries = new Map<string, TextEntry>()
  for (const msg of data.messages) {
    const key = queryKey(msg.text, msg.namespace)
    if (!uniqueQueries.has(key)) {
      uniqueQueries.set(key, msg)
    }
  }

  // Run all unique Vectorize queries in parallel
  const scoreMap = new Map<string, number>()
  await Promise.all(
    [...uniqueQueries.entries()].map(async ([key, { text, namespace }]) => {
      const vector = embeddingMap.get(text)!
      const score = await querySimilarity(c.env.VECTORIZE_INDEX, vector, namespace)
      scoreMap.set(key, score)
    })
  )

  // Map results back to the original request order
  const results = data.messages.map((msg) => ({
    similarity_score: scoreMap.get(queryKey(msg.text, msg.namespace)) || 0,
  }))

  return c.json({ results })
})

export default app
