import { Hono } from "hono"
import pLimit from "p-limit"

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
  BATCH_PROCESS_LIMIT: number
  MAX_CONCURRENT_REQUESTS: number // Add a limit for concurrent API requests
  RETRY_LIMIT: number // Number of retries for failed requests
}

type TextEntry = {
  text: string
  namespace: string
}

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

// Retry wrapper for API calls
async function retry(fn: () => Promise<any>, retries: number) {
  let lastError
  for (let i = 0; i < retries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      await new Promise(res => setTimeout(res, Math.pow(2, i) * 100)) // Exponential backoff
    }
  }
  throw lastError
}

// Process a batch of text records
async function processBatch(entries: TextEntry[], env: Env) {
  const limit = pLimit(env.MAX_CONCURRENT_REQUESTS)
  const similarityScores = await Promise.all(entries.map(entry => limit(async () => {
    const { text, namespace } = entry

    if (typeof text !== "string" || typeof namespace !== "string") {
      return { error: "Invalid JSON format" }
    }

    const modelResp = await retry(() => env.AI.run("@cf/baai/bge-base-en-v1.5", { text: [text] }), env.RETRY_LIMIT)
    const vector = modelResp.data[0]
    const searchResponse = await retry(() => env.VECTORIZE_INDEX.query(vector, { namespace, topK: 1 }), env.RETRY_LIMIT)
    const similarityScore = searchResponse.matches[0]?.score || 0
    return { similarity_score: similarityScore }
  })))

  return similarityScores
}

app.post("/", async (c) => {
  const data = await c.req.json<TextEntry[]>()
  const { BATCH_PROCESS_LIMIT } = c.env
  
  const batches = []
  for (let i = 0; i < data.length; i += BATCH_PROCESS_LIMIT) {
    batches.push(data.slice(i, i + BATCH_PROCESS_LIMIT))
  }

  const batchResults = await Promise.all(batches.map(batch => processBatch(batch, c.env)))

  return c.json(batchResults.flat())
})

export default app
