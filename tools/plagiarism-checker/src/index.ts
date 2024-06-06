import { Hono } from "hono"

interface SearchResult {
  title?: string | null
  link?: string | null
}

interface SearchResponse {
  items: Array<SearchResult>;
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
    .filter((sentence) => sentence.trim().length > 4)

  const plagiarismResults = await Promise.all(
    sentences.map(async (sentence) => {
      const query = encodeURIComponent(sentence.trim())
      const url = `https://www.googleapis.com/customsearch/v1?exactTerms=${query}&key=${c.env.GOOGLE_API_KEY}&cx=${c.env.GOOGLE_SEARCH_ENGINE_CX}&num=10`

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

  const plagiarism_count = plagiarismResults.reduce((total, current) => {
    if (current.matches.length > 0) {
      total++
    }
    return total
  }, 0)

  const plagiarism_percent = plagiarism_count
    ? (sentences.length / plagiarism_count) * 100
    : 0

  return c.json({ plagiarism_percent, results: plagiarismResults })
})

export default app
