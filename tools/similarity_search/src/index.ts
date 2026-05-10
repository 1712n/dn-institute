import { Hono } from "hono"

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
}

type EmbeddingResponse = {
  data?: unknown[]
}

const app = new Hono<{ Bindings: Env }>()

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
}

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
  let data: unknown
  try {
    data = await c.req.json()
  } catch {
    return c.text("Invalid JSON format", 400)
  }

  if (!isRecord(data)) {
    return c.text("Invalid JSON format", 400)
  }

  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const modelResp = (await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: [text]
  })) as EmbeddingResponse
  const vector = modelResp.data?.[0]

  if (!Array.isArray(vector)) {
    return c.text("Embedding not found", 502)
  }

  const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
    namespace,
    topK: 1
  })
  const similarityScore = searchResponse.matches[0]?.score || 0

  return c.json({ similarity_score: similarityScore })
})

export default app
