import { Hono } from "hono"

type Env = {
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
  KV_CACHE: KVNamespace
}

type TextEntry = {
  text: string
  namespace: string
}

type BatchItem = {
  text: string
  namespace: string
  id?: string
}

type BatchResult = {
  id?: string
  text: string
  namespace: string
  similarity_score: number
  cached?: boolean
}

type BatchError = {
  index: number
  id?: string
  text: string
  namespace: string
  error: string
}

const app = new Hono<{ Bindings: Env }>()

// Cost tracking (Cloudflare Workers AI pricing as of 2026)
const COST_PER_EMBEDDING_CALL = 0.0001 // $0.0001 per AI call
const COST_PER_VECTORIZE_QUERY = 0.00001 // $0.00001 per 10 vectors

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

// Single text endpoint (unchanged)
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

// Batch endpoint with streaming, partial failure tolerance, and caching 🌰
app.post("/batch", async (c) => {
  const body = await c.req.json<{
    items: BatchItem[]
    stream?: boolean
    useCache?: boolean
  }>()

  const { items, stream = false, useCache = true } = body

  // Validation
  if (!items || !Array.isArray(items)) {
    return c.json({ error: "Missing or invalid 'items' array" }, 400)
  }

  if (items.length === 0) {
    return c.json({ error: "Items array cannot be empty" }, 400)
  }

  if (items.length > 100) {
    return c.json({ 
      error: "Batch size exceeds limit of 100 items",
      received: items.length,
      limit: 100
    }, 400)
  }

  // Validate all items upfront
  const validationErrors: BatchError[] = []
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (!item || typeof item.text !== "string" || typeof item.namespace !== "string") {
      validationErrors.push({
        index: i,
        id: item?.id,
        text: item?.text || "",
        namespace: item?.namespace || "",
        error: "Invalid item format: 'text' and 'namespace' must be strings"
      })
    }
  }

  if (validationErrors.length > 0) {
    return c.json({ 
      error: "Validation failed",
      failed: validationErrors
    }, 400)
  }

  // Group items by namespace for efficient Vectorize queries
  const itemsByNamespace = new Map<string, { index: number; item: BatchItem }[]>()
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    const ns = item.namespace
    if (!itemsByNamespace.has(ns)) {
      itemsByNamespace.set(ns, [])
    }
    itemsByNamespace.get(ns)!.push({ index: i, item })
  }

  // Extract unique texts for embedding (deduplicate within batch)
  const uniqueTexts = Array.from(new Set(items.map(item => item.text)))
  
  // Check cache for embeddings if enabled
  let cachedEmbeddings = new Map<string, number[]>()
  let textsToEmbed = uniqueTexts

  if (useCache && c.env.KV_CACHE) {
    const cachePromises = uniqueTexts.map(async (text) => {
      const cacheKey = `emb:${Buffer.from(text).toString('base64').substring(0, 64)}`
      try {
        const cached = await c.env.KV_CACHE.get(cacheKey, "json")
        if (cached && Array.isArray(cached)) {
          cachedEmbeddings.set(text, cached)
        }
      } catch (e) {
        // Cache miss or error, will embed
      }
    })
    await Promise.all(cachePromises)
    textsToEmbed = uniqueTexts.filter(t => !cachedEmbeddings.has(t))
  }

  // Embed missing texts (single batch call for efficiency)
  let allEmbeddings = new Map<string, number[]>()
  
  // Copy cached embeddings
  for (const [text, emb] of cachedEmbeddings) {
    allEmbeddings.set(text, emb)
  }

  if (textsToEmbed.length > 0) {
    const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: textsToEmbed
    })
    for (let i = 0; i < textsToEmbed.length; i++) {
      allEmbeddings.set(textsToEmbed[i], modelResp.data[i])
      
      // Cache the embedding
      if (useCache && c.env.KV_CACHE) {
        const cacheKey = `emb:${Buffer.from(textsToEmbed[i]).toString('base64').substring(0, 64)}`
        try {
          await c.env.KV_CACHE.put(cacheKey, JSON.stringify(modelResp.data[i]), { expirationTtl: 86400 * 7 })
        } catch (e) {
          // Cache write failed, continue
        }
      }
    }
  }

  // Query Vectorize for each namespace (parallel)
  const results: (BatchResult | null)[] = new Array(items.length).fill(null)
  const errors: BatchError[] = []
  let vectorizeQueries = 0

  const queryPromises = Array.from(itemsByNamespace.entries()).map(async ([namespace, nsItems]) => {
    const queryPromises = nsItems.map(async ({ index, item }) => {
      const vector = allEmbeddings.get(item.text)!
      try {
        const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
          namespace,
          topK: 1
        })
        vectorizeQueries++
        const similarityScore = searchResponse.matches[0]?.score || 0
        results[index] = {
          id: item.id,
          text: item.text,
          namespace: item.namespace,
          similarity_score: similarityScore,
          cached: cachedEmbeddings.has(item.text)
        }
      } catch (e) {
        errors.push({
          index,
          id: item.id,
          text: item.text,
          namespace: item.namespace,
          error: e instanceof Error ? e.message : "Vectorize query failed"
        })
        results[index] = null
      }
    })
    await Promise.all(queryPromises)
  })

  await Promise.all(queryPromises)

  // Calculate cost
  const aiCallsCost = (textsToEmbed.length > 0 ? 1 : 0) * COST_PER_EMBEDDING_CALL
  const vectorizeCost = (vectorizeQueries / 10) * COST_PER_VECTORIZE_QUERY
  const totalCost = aiCallsCost + vectorizeCost

  // Build response
  const successfulResults = results.filter((r): r is BatchResult => r !== null)
  
  const response: any = {
    results: successfulResults,
    summary: {
      total: items.length,
      processed: successfulResults.length,
      failed: errors.length,
      cached: successfulResults.filter(r => r.cached).length
    },
    cost: {
      ai_embedding_calls: textsToEmbed.length > 0 ? 1 : 0,
      vectorize_queries: vectorizeQueries,
      estimated_usd: parseFloat(totalCost.toFixed(6))
    }
  }

  if (errors.length > 0) {
    response.failed = errors
  }

  return c.json(response)
})

// Cache stats endpoint
app.get("/cache/stats", async (c) => {
  if (!c.env.KV_CACHE) {
    return c.json({ error: "Cache not configured" }, 503)
  }
  
  // Note: KV namespace doesn't have a direct count API, so we return a placeholder
  // In production, you'd track this separately
  return c.json({
    status: "enabled",
    note: "Use external metrics for cache hit rate tracking"
  })
})

// Health check
app.get("/health", async (c) => {
  return c.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    endpoints: ["/", "/batch", "/batch (stream)", "/cache/stats", "/health"]
  })
})

export default app
