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

type BatchEntry = {
  text: string
}

type BatchRequest = {
  namespace: string
  texts: string[]
} & Partial<{
  topK: number
}>

type BatchRequestObjects = {
  namespace: string
  entries: BatchEntry[]
} & Partial<{
  topK: number
}>

const app = new Hono<{ Bindings: Env }>()

const MAX_BATCH_SIZE = 50
const DEFAULT_TOPK = 1
const MAX_TOPK = 10

function isNonEmptyString(v: unknown): v is string {
  return typeof v === "string" && v.length > 0
}

function clampInt(n: unknown, min: number, max: number, fallback: number): number {
  if (typeof n !== "number" || !Number.isFinite(n)) return fallback
  const i = Math.trunc(n)
  if (i < min) return min
  if (i > max) return max
  return i
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

app.post("/batch", async (c) => {
  const raw = await c.req.json<BatchRequest | BatchRequestObjects>()

  const namespace = (raw as any)?.namespace
  const topK = clampInt((raw as any)?.topK, 1, MAX_TOPK, DEFAULT_TOPK)

  if (!isNonEmptyString(namespace)) {
    return c.text("Invalid JSON format", 400)
  }

  let texts: unknown[] | undefined = undefined
  if (Array.isArray((raw as any)?.texts)) {
    texts = (raw as any).texts
  } else if (Array.isArray((raw as any)?.entries)) {
    texts = (raw as any).entries.map((e: any) => e?.text)
  }

  if (!texts || !Array.isArray(texts)) {
    return c.text("Invalid JSON format", 400)
  }

  if (texts.length === 0) {
    return c.json({ namespace, topK, results: [] })
  }

  if (texts.length > MAX_BATCH_SIZE) {
    return c.text("Batch size too large", 413)
  }

  const normalizedTexts: string[] = new Array(texts.length)
  for (let i = 0; i < texts.length; i++) {
    const t = texts[i]
    if (typeof t !== "string") {
      return c.text("Invalid JSON format", 400)
    }
    normalizedTexts[i] = t
  }

  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: normalizedTexts
  })

  const vectors: unknown[] = Array.isArray((modelResp as any)?.data) ? (modelResp as any).data : []
  if (vectors.length !== normalizedTexts.length) {
    return c.text("Upstream embedding error", 502)
  }

  const queries = vectors.map((vector, i) =>
    c.env.VECTORIZE_INDEX
      .query(vector as any, { namespace, topK })
      .then((searchResponse: any) => {
        const matches = Array.isArray(searchResponse?.matches) ? searchResponse.matches : []
        return {
          index: i,
          text: normalizedTexts[i],
          similarity_score: matches[0]?.score || 0
        }
      })
  )

  const results = await Promise.all(queries)
  return c.json({ namespace, topK, results })
})

export default app
