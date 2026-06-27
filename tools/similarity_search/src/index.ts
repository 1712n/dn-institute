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

  if (
    typeof text !== "string" ||
    text.trim() === "" ||
    typeof namespace !== "string"
  ) {
    return c.text("Invalid JSON format", 400)
  }

  let vector
  try {
    const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: [text]
    })

    vector = modelResp.data?.[0]
    if (
      !Array.isArray(vector) ||
      vector.length === 0 ||
      vector.some((value) => typeof value !== "number" || !Number.isFinite(value))
    ) {
      throw new Error("Workers AI returned invalid response shape")
    }
  } catch (error) {
    console.error("Workers AI request failed", error)
    return c.text("Workers AI request failed", 502)
  }

  let searchResponse
  try {
    searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
      namespace,
      topK: 1
    })

    if (!Array.isArray(searchResponse?.matches)) {
      throw new Error("Vectorize returned invalid response shape")
    }
  } catch (error) {
    console.error("Vectorize query failed", error)
    return c.text("Vectorize query failed", 502)
  }
  const similarityScore = searchResponse.matches[0]?.score || 0

  return c.json({ similarity_score: similarityScore })
})

export default app
