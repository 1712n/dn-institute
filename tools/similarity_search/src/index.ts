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

type BatchResult = {
  similarity_score: number
}

const MAX_BATCH_SIZE = 100
const VECTORIZE_QUERY_CONCURRENCY = 10
const EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"

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

function isValidTextEntry(value: unknown): value is TextEntry {
  if (typeof value !== "object" || value === null) {
    return false
  }

  const entry = value as Partial<TextEntry>
  return typeof entry.text === "string" && entry.text.length > 0
    && typeof entry.namespace === "string" && entry.namespace.length > 0
}

function isEmbeddingVector(value: unknown): value is number[] {
  return Array.isArray(value)
    && value.every((entry) => typeof entry === "number" && Number.isFinite(entry))
}

async function readJson<T>(request: Request): Promise<T | null> {
  try {
    return await request.json<T>()
  } catch {
    return null
  }
}

async function embedTexts(ai: Ai, texts: string[]): Promise<number[][]> {
  const modelResp = await ai.run(EMBEDDING_MODEL, { text: texts }) as { data?: unknown }
  const embeddings = modelResp.data

  if (!Array.isArray(embeddings) || embeddings.length !== texts.length) {
    throw new Error("Embedding response size did not match request size")
  }

  return embeddings.map((embedding, index) => {
    if (!isEmbeddingVector(embedding)) {
      throw new Error(`Embedding response contained invalid vector at index ${index}`)
    }

    return embedding
  })
}

async function querySimilarity(env: Env, item: TextEntry, vector: number[]): Promise<BatchResult> {
  const searchResponse = await env.VECTORIZE_INDEX.query(vector, {
    namespace: item.namespace,
    topK: 1
  })
  const similarityScore = searchResponse.matches[0]?.score || 0

  return { similarity_score: similarityScore }
}

async function querySimilarities(env: Env, items: TextEntry[], vectors: number[][]): Promise<BatchResult[]> {
  const results: BatchResult[] = []

  for (let i = 0; i < items.length; i += VECTORIZE_QUERY_CONCURRENCY) {
    const itemChunk = items.slice(i, i + VECTORIZE_QUERY_CONCURRENCY)
    const vectorChunk = vectors.slice(i, i + VECTORIZE_QUERY_CONCURRENCY)
    const chunkResults = await Promise.all(
      itemChunk.map((item, index) => querySimilarity(env, item, vectorChunk[index]))
    )
    results.push(...chunkResults)
  }

  return results
}

app.post("/", async (c) => {
  const data = await readJson<TextEntry>(c.req.raw)

  if (!isValidTextEntry(data)) {
    return c.text("Invalid JSON format", 400)
  }

  try {
    const [vector] = await embedTexts(c.env.AI, [data.text])
    const result = await querySimilarity(c.env, data, vector)

    return c.json(result)
  } catch (error) {
    return c.text(error instanceof Error ? error.message : "Similarity lookup failed", 502)
  }
})

app.post("/batch", async (c) => {
  const data = await readJson<Partial<BatchRequest>>(c.req.raw)

  if (typeof data !== "object" || data === null || !Array.isArray(data.items)) {
    return c.text("Invalid JSON format", 400)
  }

  if (data.items.length === 0 || data.items.length > MAX_BATCH_SIZE) {
    return c.text(`Batch size must be between 1 and ${MAX_BATCH_SIZE}`, 400)
  }

  if (!data.items.every(isValidTextEntry)) {
    return c.text("Invalid JSON format", 400)
  }

  try {
    const vectors = await embedTexts(c.env.AI, data.items.map((item) => item.text))
    const results = await querySimilarities(c.env, data.items, vectors)

    return c.json({ results })
  } catch (error) {
    return c.text(error instanceof Error ? error.message : "Batch processing failed", 502)
  }
})

export default app
