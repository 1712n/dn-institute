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

type EmbeddingResponse = {
  data?: unknown[]
}

const isEmbeddingVector = (value: unknown): value is number[] =>
  Array.isArray(value) &&
  value.length > 0 &&
  value.every((item) => typeof item === "number" && Number.isFinite(item))

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

  let modelResp: EmbeddingResponse
  try {
    const response = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: [text]
    })
    modelResp = response as unknown as EmbeddingResponse
  } catch {
    return c.text("Embedding generation failed", 502)
  }

  const vector = modelResp.data?.[0]
  if (!isEmbeddingVector(vector)) {
    return c.text("Embedding generation failed", 502)
  }

  let searchResponse: Awaited<ReturnType<Env["VECTORIZE_INDEX"]["query"]>>
  try {
    searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
      namespace,
      topK: 1
    })
  } catch {
    return c.text("Similarity search failed", 502)
  }
  const similarityScore = searchResponse.matches[0]?.score || 0

  return c.json({ similarity_score: similarityScore })
})

export default app
