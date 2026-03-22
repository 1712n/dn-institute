import { Hono } from "hono"
import type { Env, IssueCommentEvent } from "./types"
import {
  verifyWebhookSignature,
  fetchPRDiff,
  parseDiff,
  removePlus,
  postPRComment,
} from "./github"
import { checkArticle } from "./claude"

const app = new Hono<{ Bindings: Env }>()

/**
 * Health check endpoint.
 */
app.get("/", (c) => {
  return c.json({ status: "ok", service: "article-checker-worker" })
})

/**
 * GitHub webhook endpoint.
 * Handles issue_comment events triggered by /articlecheck commands on PRs.
 */
app.post("/webhook", async (c) => {
  const body = await c.req.text()

  // Verify webhook signature for security
  const signature = c.req.header("x-hub-signature-256") || null
  const isValid = await verifyWebhookSignature(
    body,
    signature,
    c.env.WEBHOOK_SECRET
  )
  if (!isValid) {
    return c.json({ error: "Invalid webhook signature" }, 401)
  }

  // Only handle issue_comment events
  const event = c.req.header("x-github-event")
  if (event !== "issue_comment") {
    return c.json({ message: "Event ignored" }, 200)
  }

  const payload: IssueCommentEvent = JSON.parse(body)

  // Only handle newly created comments
  if (payload.action !== "created") {
    return c.json({ message: "Action ignored" }, 200)
  }

  // Only handle comments on pull requests
  if (!payload.issue.pull_request) {
    return c.json({ message: "Not a PR comment" }, 200)
  }

  // Only handle /articlecheck commands
  if (!payload.comment.body.includes("/articlecheck")) {
    return c.json({ message: "Not an articlecheck command" }, 200)
  }

  // Permission check: verify commenter is in WIKI_REVIEWERS list
  let reviewers: string[] = []
  try {
    reviewers = JSON.parse(c.env.WIKI_REVIEWERS)
  } catch {
    return c.json({ error: "Invalid WIKI_REVIEWERS configuration" }, 500)
  }

  const commenter = payload.comment.user.login
  if (!reviewers.includes(commenter)) {
    return c.json({ message: "User not authorized" }, 403)
  }

  const owner = payload.repository.owner.login
  const repo = payload.repository.name
  const prNumber = payload.issue.number

  // Process asynchronously using waitUntil so we respond to GitHub quickly
  // (GitHub expects a response within 10 seconds)
  c.executionCtx.waitUntil(
    processArticleCheck(
      owner,
      repo,
      prNumber,
      c.env.GITHUB_TOKEN,
      c.env.LLM_API_KEY,
      c.env.SEARCH_API_KEY
    )
  )

  return c.json({ message: "Article check started" }, 202)
})

/**
 * Core processing logic: fetch diff, run checks, post results.
 */
async function processArticleCheck(
  owner: string,
  repo: string,
  prNumber: number,
  githubToken: string,
  llmApiKey: string,
  searchApiKey: string
): Promise<void> {
  try {
    // Fetch the PR diff
    const rawDiff = await fetchPRDiff(owner, repo, prNumber, githubToken)

    // Parse the diff into structured files
    const files = parseDiff(rawDiff)

    if (files.length === 0) {
      await postPRComment(
        owner,
        repo,
        prNumber,
        "⚠️ No files found in the PR diff to check.",
        githubToken
      )
      return
    }

    // Extract the article text from the first file's diff
    // (matching the Python behavior: diff[0]['header'] + diff[0]['body'][0]['body'])
    const firstFile = files[0]
    const articleText =
      firstFile.body.length > 0
        ? removePlus(firstFile.header + firstFile.body[0].body)
        : removePlus(firstFile.header)

    if (!articleText.trim()) {
      await postPRComment(
        owner,
        repo,
        prNumber,
        "⚠️ No article content found in the PR diff.",
        githubToken
      )
      return
    }

    // Run the article check pipeline
    const answer = await checkArticle(articleText, llmApiKey, searchApiKey)

    // Post the result as a PR comment
    await postPRComment(owner, repo, prNumber, answer, githubToken)
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error"
    console.error(`Article check failed: ${errorMessage}`)

    try {
      await postPRComment(
        owner,
        repo,
        prNumber,
        `❌ Article check failed: ${errorMessage}`,
        githubToken
      )
    } catch (commentError) {
      console.error(`Failed to post error comment: ${commentError}`)
    }
  }
}

export default app
