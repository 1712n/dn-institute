import { Hono } from "hono"

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
  MAX_INPUT: number
}

type TextEntry = {
  text: string | string[]
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

  let texts: string[]
  if (typeof text === "string") {
    texts = [text]
  } else if (Array.isArray(data.text) && data.text.every((element) => typeof element === "string")) {
    texts = text
  } else {
    return c.text("Invalid JSON format, property `text` must be a string or array of strings", 400)
  }
  const MAX_INPUT = Number(c.env.MAX_INPUT) || 100
  if (texts.length > MAX_INPUT) {
    return c.text(`Too big input, property \`text\` can have max ${MAX_INPUT} items`, 400)
  }
  if (typeof namespace !== "string") {
    return c.text("Invalid JSON format, property `namespace` must be a string", 400)
  }

  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: texts
  })

  let index = 0
  const requests = texts.map((text) => {
    const vector = modelResp.data[index++]
    return c.env.VECTORIZE_INDEX.query(vector, {
      namespace,
      topK: 1
    })
  })
  const responses = await Promise.all(requests)
  const similarityScores = []
  for (const searchResponse of responses) {
    const similarityScore = searchResponse.matches[0]?.score || 0
    similarityScores.push(similarityScore)
  }

  if (typeof text === 'string') {
    return c.json({ similarity_score: similarityScores[0] })
  } else {
    return c.json({ similarity_score: similarityScores })
  }
})

export default app
