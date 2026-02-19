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
  const data = await c.req.json<TextEntry | TextEntry[]>()

  // 🌰 Chipmunk logic for batch processing starts here 🌰
  const isBatch = Array.isArray(data)
  const entries = isBatch ? data : [data]

  if (entries.length === 0) {
    return c.text("Empty batch 🌰", 400)
  }

  for (const entry of entries) {
    if (typeof entry.text !== "string" || typeof entry.namespace !== "string") {
      return c.text("Invalid JSON format 🌰", 400)
    }
  }

  const texts = entries.map((e) => e.text)

  // 🌰 Leveraging Cloudflare Workers AI batch inference for resource efficiency 🌰
  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })

  const results = await Promise.all(
    entries.map(async (entry, index) => {
      const vector = modelResp.data[index]
      // 🌰 Native Vectorize query for high-speed similarity search 🌰
      const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
        namespace: entry.namespace,
        topK: 1
      })
      return {
        similarity_score: searchResponse.matches[0]?.score || 0
      }
    })
  )

  return isBatch ? c.json(results) : c.json(results[0])
})

export default app
