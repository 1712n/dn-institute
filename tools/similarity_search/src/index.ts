import { Hono } from "hono"

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
  BATCH_PROCESS_LIMIT: number // batch size controller
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

// batch texts records package 
async function processBatch(entries: TextEntry[], env: Env) {
  const similarityScores = await Promise.all(entries.map(async entry => {
    const { text, namespace } = entry

    if (typeof text !== "string" || typeof namespace !== "string") {
      return { error: "Invalid JSON format" }
    }

    const modelResp = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: [text]
    })
    const vector = modelResp.data[0]
    const searchResponse = await env.VECTORIZE_INDEX.query(vector, {
      namespace,
      topK: 1
    })
    const similarityScore = searchResponse.matches[0]?.score || 0
    return { similarity_score: similarityScore }
  }))

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
