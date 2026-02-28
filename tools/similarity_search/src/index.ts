import { Hono } from "hono"

// 🌰 Types for the similarity search API

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
}

/** Single text+namespace entry for similarity search */
type TextEntry = {
  text: string
  namespace: string
}

/** 🌰 Request body for the batch endpoint */
export type BatchRequest = {
  items: TextEntry[]
}

/** 🌰 Individual result from a batch similarity search */
export type BatchResultItem = {
  text: string
  namespace: string
  similarity_score: number
}

/** 🌰 Response from the batch endpoint */
export type BatchResponse = {
  results: BatchResultItem[]
}

/** 🌰 Structured error response for validation failures */
export type ErrorResponse = {
  error: string
  code: string
  details?: string
}

/**
 * 🌰 Maximum number of items allowed in a single batch request.
 * Prevents excessive resource usage per request.
 */
const MAX_BATCH_SIZE = 100

/**
 * 🌰 Maximum character length for individual text entries.
 * Aligns with typical embedding model input limits.
 */
const MAX_TEXT_LENGTH = 10_000

/**
 * 🌰 Number of texts to embed per Workers AI call.
 * Cloudflare Workers AI has limits on batch embedding sizes.
 */
const EMBEDDING_BATCH_LIMIT = 100

const app = new Hono<{ Bindings: Env }>()

// 🌰 Authentication middleware — shared across all endpoints
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

// 🌰 Original single-item endpoint — preserved for backward compatibility
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

/**
 * 🌰 Batch similarity search endpoint.
 *
 * Accepts multiple text+namespace pairs and returns similarity scores
 * for each. Optimizes performance via batched embedding generation
 * and parallel Vectorize queries grouped by namespace.
 */
app.post("/batch", async (c) => {
  // 🌰 Parse and validate request body
  let body: BatchRequest
  try {
    body = await c.req.json<BatchRequest>()
  } catch {
    return c.json<ErrorResponse>(
      { error: "Invalid JSON body", code: "INVALID_JSON" },
      400
    )
  }

  // 🌰 Validate items array exists and is an array
  if (!body.items || !Array.isArray(body.items)) {
    return c.json<ErrorResponse>(
      {
        error: "Request must contain an 'items' array",
        code: "MISSING_ITEMS"
      },
      400
    )
  }

  // 🌰 Validate batch is non-empty
  if (body.items.length === 0) {
    return c.json<ErrorResponse>(
      { error: "Batch must contain at least one item", code: "EMPTY_BATCH" },
      400
    )
  }

  // 🌰 Validate batch size limit
  if (body.items.length > MAX_BATCH_SIZE) {
    return c.json<ErrorResponse>(
      {
        error: `Batch size exceeds maximum of ${MAX_BATCH_SIZE} items`,
        code: "BATCH_TOO_LARGE",
        details: `Received ${body.items.length} items`
      },
      400
    )
  }

  // 🌰 Validate each item's structure
  for (let i = 0; i < body.items.length; i++) {
    const item = body.items[i]

    if (typeof item.text !== "string" || typeof item.namespace !== "string") {
      return c.json<ErrorResponse>(
        {
          error: `Invalid item at index ${i}: 'text' and 'namespace' must be strings`,
          code: "INVALID_ITEM",
          details: `Index ${i}`
        },
        400
      )
    }

    if (item.text.length === 0) {
      return c.json<ErrorResponse>(
        {
          error: `Empty text at index ${i}`,
          code: "EMPTY_TEXT",
          details: `Index ${i}`
        },
        400
      )
    }

    if (item.text.length > MAX_TEXT_LENGTH) {
      return c.json<ErrorResponse>(
        {
          error: `Text at index ${i} exceeds maximum length of ${MAX_TEXT_LENGTH} characters`,
          code: "TEXT_TOO_LONG",
          details: `Index ${i}, length ${item.text.length}`
        },
        400
      )
    }
  }

  // 🌰 Step 1: Generate embeddings in chunks of EMBEDDING_BATCH_LIMIT
  const allTexts = body.items.map((item) => item.text)
  const allVectors: number[][] = []

  for (let i = 0; i < allTexts.length; i += EMBEDDING_BATCH_LIMIT) {
    const chunk = allTexts.slice(i, i + EMBEDDING_BATCH_LIMIT)
    const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: chunk
    })
    allVectors.push(...modelResp.data)
  }

  // 🌰 Step 2: Group items by namespace for efficient Vectorize queries
  const namespaceGroups = new Map<
    string,
    { originalIndex: number; vector: number[] }[]
  >()

  for (let i = 0; i < body.items.length; i++) {
    const ns = body.items[i].namespace
    if (!namespaceGroups.has(ns)) {
      namespaceGroups.set(ns, [])
    }
    namespaceGroups.get(ns)!.push({ originalIndex: i, vector: allVectors[i] })
  }

  // 🌰 Step 3: Query Vectorize in parallel, one query per item but grouped by namespace
  const results: BatchResultItem[] = new Array(body.items.length)

  const queryPromises: Promise<void>[] = []

  for (const [namespace, entries] of namespaceGroups) {
    for (const entry of entries) {
      const promise = c.env.VECTORIZE_INDEX.query(entry.vector, {
        namespace,
        topK: 1
      }).then((searchResponse) => {
        const score = searchResponse.matches[0]?.score || 0
        results[entry.originalIndex] = {
          text: body.items[entry.originalIndex].text,
          namespace,
          similarity_score: score
        }
      })
      queryPromises.push(promise)
    }
  }

  await Promise.all(queryPromises)

  // 🌰 Return results preserving original request order
  return c.json<BatchResponse>({ results })
})

export default app
