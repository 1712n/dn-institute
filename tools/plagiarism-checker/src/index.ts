import { Hono } from "hono"

interface SearchResult {
  title?: string | null
  link?: string | null
}

interface SearchResponse {
  items: Array<SearchResult>
}

type Env = {
  GOOGLE_API_KEY: string
  GOOGLE_SEARCH_ENGINE_CX: string
}

const app = new Hono<{ Bindings: Env }>()

app.use("*", async (c, next) => {
  const apiKey = c.env.GOOGLE_API_KEY
  if (!apiKey) {
    return c.text("API key not found", 400)
  }

  const searchEngine = c.env.GOOGLE_SEARCH_ENGINE_CX
  if (!searchEngine) {
    return c.text("Search engine not specified", 400)
  }

  return next()
})

app.post("/", async (c) => {
  const { text } = await c.req.json()

  if (typeof text !== "string") {
    return c.json({ error: "Invalid JSON format" }, 400)
  }

  const sentences = text
    .split(".")
    // if it's less than 10 characters - we don't treat it as a sentence and skip it
    .filter((sentence) => sentence.trim().length > 10)

  const plagiarismResults = await Promise.all(
    sentences.map(async (sentence) => {
      const query = encodeURIComponent(sentence.trim())
      const url = `https://www.googleapis.com/customsearch/v1?exactTerms=${query}&key=${c.env.GOOGLE_API_KEY}&cx=${c.env.GOOGLE_SEARCH_ENGINE_CX}&num=1`
      const response = await fetch(url)
      const searchResults: SearchResponse = await response.json()

      return {
        sentence,
        matches: searchResults.items
          ? searchResults.items.map((item: SearchResult) => ({
              title: item.title,
              link: item.link
            }))
          : []
      }
    })
  )

  const plagiarisedSentencesNumber = plagiarismResults.reduce(
    (total, current) => {
      if (current.matches.length > 0) {
        total++
      }
      return total
    },
    0
  )

  const plagiarismPercent = plagiarisedSentencesNumber
    ? (sentences.length / plagiarisedSentencesNumber) * 100
    : 0

  return c.json({ plagiarismPercent, results: plagiarismResults })
})

export default app
