import { Hono } from "hono"

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
  // Format https://gateway.ai.cloudflare.com/v1/{ACCOUNT_ID}/{SLUG}/
  const apiGatewayUniversalApi = c.env.API_GATEWAY_UNIVERSAL_API
  if (!apiGatewayUniversalApi) {
    return c.text("Missing gateway URL", 500)
  }

  const workersApikey = c.env.WORKERS_API_KEY
  if (!workersApikey) {
    return c.text("Missing workers API key", 500)
  }

  let data: TextEntry
  try {
    data = await c.req.json<TextEntry>()
  } catch (error) {
    return c.text("Cannot parse JSON input", 400)
  }

  const { text, namespace } = data

  let texts: string[]
  if (typeof text === "string" && text.length) {
    texts = [text]
  } else if (
    Array.isArray(text) &&
    text.every((element) => typeof element === "string" && element.length)
  ) {
    texts = text
  } else {
    return c.text(
      "Invalid JSON format, property `text` must be a non-empty string or array of non-empty strings",
      400,
    )
  }
  const MAX_INPUT = Number(c.env.MAX_INPUT) || 100
  if (texts.length > MAX_INPUT) {
    return c.text(
      `Too big input, property \`text\` can have max ${MAX_INPUT} items`,
      400,
    )
  }
  if (typeof namespace !== "string") {
    return c.text(
      "Invalid JSON format, property `namespace` must be a string",
      400,
    )
  }

  // resolve each text individually to enable cache per request
  const requests = texts.map((text) => {
    return fetch(
      `${apiGatewayUniversalApi}workers-ai/@cf/baai/bge-base-en-v1.5`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${workersApikey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
        }),
      },
    )
      .then((response) => response.json())
      .then((response) => {
        console.log("Gateway response", response)
        // TODO - type
        const vector = response?.result?.data?.[0]
        return c.env.VECTORIZE_INDEX.query(vector, {
          namespace,
          topK: 1,
        })
      })
  })
  const responses = await Promise.all(requests)
  const similarityScores = []
  for (const searchResponse of responses) {
    const similarityScore = searchResponse.matches[0]?.score || 0
    similarityScores.push(similarityScore)
  }

  if (typeof text === "string") {
    return c.json({ similarity_score: similarityScores[0] })
  } else {
    return c.json({ similarity_score: similarityScores })
  }
})

export default app
