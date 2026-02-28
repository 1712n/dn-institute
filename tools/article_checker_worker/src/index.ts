/**
 * 🌰 Article Checker Worker
 *
 * Cloudflare Worker that processes GitHub webhook events for article fact-checking.
 * Triggered by /articlecheck comments on pull requests.
 *
 * Architecture: Single worker with Hono router, using waitUntil() for async processing.
 * Responds 200 immediately to the webhook, then processes in the background.
 */

import { Hono } from "hono"
import type { Env, GitHubWebhookPayload } from "./types"
import { verifySignature } from "./crypto"
import {
  isAllowedReviewer,
  validateWebhookPayload,
  fetchPRDiff,
  parseDiff,
  postPRComment,
  postCommentReaction,
} from "./github"
import { runPipeline } from "./pipeline"

type HonoEnv = { Bindings: Env }

const app = new Hono<HonoEnv>()

// ─── Health check ────────────────────────────────────────────────────────────

app.get("/", (c) => {
  return c.json({
    status: "ok",
    service: "article-checker-worker",
    version: "1.0.0",
  })
})

// ─── Webhook endpoint ────────────────────────────────────────────────────────

app.post("/webhook", async (c) => {
  const body = await c.req.text()

  // 🌰 Step 1: Verify webhook signature (HMAC-SHA256)
  const signature = c.req.header("X-Hub-Signature-256") ?? ""
  const isValid = await verifySignature(body, signature, c.env.WEBHOOK_SECRET)
  if (!isValid) {
    return c.json({ error: "Invalid signature" }, 401)
  }

  // 🌰 Step 2: Parse and validate payload
  let payload: GitHubWebhookPayload
  try {
    payload = JSON.parse(body)
  } catch {
    return c.json({ error: "Invalid JSON" }, 400)
  }

  const validation = validateWebhookPayload(payload)
  if (!validation.valid) {
    return c.json({ status: "skipped", reason: validation.reason }, 200)
  }

  // 🌰 Step 3: Check reviewer allowlist
  const commenter = payload.comment!.user.login
  if (!isAllowedReviewer(commenter, c.env.REVIEWER_ALLOWLIST)) {
    return c.json({ status: "skipped", reason: "User not in reviewer allowlist" }, 200)
  }

  const owner = payload.repository.owner.login
  const repo = payload.repository.name
  const prNumber = validation.prNumber
  const commentId = payload.comment!.id

  // 🌰 Step 4: Respond immediately, process asynchronously via waitUntil()
  c.executionCtx.waitUntil(
    processArticleCheck(
      owner,
      repo,
      prNumber,
      commentId,
      c.env.GITHUB_TOKEN,
      c.env.ANTHROPIC_API_KEY,
      c.env.BRAVE_API_KEY
    )
  )

  return c.json({ status: "processing", pr: prNumber }, 202)
})

// ─── Background processing ──────────────────────────────────────────────────

async function processArticleCheck(
  owner: string,
  repo: string,
  prNumber: number,
  commentId: number,
  githubToken: string,
  anthropicKey: string,
  braveKey: string
): Promise<void> {
  try {
    // Acknowledge with eyes reaction
    await postCommentReaction(owner, repo, commentId, "eyes", githubToken)

    // Fetch PR diff
    console.log(`🌰 Fetching diff for ${owner}/${repo}#${prNumber}`)
    const rawDiff = await fetchPRDiff(owner, repo, prNumber, githubToken)
    const files = parseDiff(rawDiff)

    if (files.length === 0) {
      await postPRComment(
        owner,
        repo,
        prNumber,
        "🌰 **Article Checker**: No markdown content found in this PR's diff.",
        githubToken
      )
      return
    }

    // Process the first content file (matching Python behavior)
    const file = files[0]
    const articleText = file.body

    // Run the 3-phase pipeline
    const review = await runPipeline(articleText, anthropicKey, braveKey)

    // Post the review as a PR comment
    const header = `## 🌰 Article Check Results\n\n**File**: \`${file.filename}\`\n\n`
    await postPRComment(owner, repo, prNumber, header + review, githubToken)

    // Add rocket reaction to indicate completion
    await postCommentReaction(owner, repo, commentId, "rocket", githubToken)

    console.log(`🌰 Article check completed for ${owner}/${repo}#${prNumber}`)
  } catch (error) {
    console.error("🌰 Article check failed:", error)

    // Post error comment
    const errorMsg =
      error instanceof Error ? error.message : "Unknown error"
    await postPRComment(
      owner,
      repo,
      prNumber,
      `🌰 **Article Checker**: Processing failed.\n\n\`\`\`\n${errorMsg}\n\`\`\``,
      githubToken
    ).catch((e) => console.error("Failed to post error comment:", e))
  }
}

export default app
