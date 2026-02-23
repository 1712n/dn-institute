import { verifySignature } from "./crypto"
import {
  fetchPrDiff,
  isArticleCheckCommand,
  isPullRequestComment,
  parseReviewers,
  postComment
} from "./github"
import { parseDiff } from "./diff"
import { runArticleCheck } from "./claude"
import type { Env, WebhookPayload } from "./types"

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    // Only accept POST requests
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 })
    }

    // Only handle issue_comment events
    const event = request.headers.get("x-github-event")
    if (event !== "issue_comment") {
      return new Response("Event not handled", { status: 200 })
    }

    // Read body for signature verification
    const body = await request.text()

    // Verify webhook signature
    const signature = request.headers.get("x-hub-signature-256") ?? ""
    const valid = await verifySignature(body, signature, env.WEBHOOK_SECRET)
    if (!valid) {
      return new Response("Invalid signature", { status: 401 })
    }

    // Parse the webhook payload
    let payload: WebhookPayload
    try {
      payload = JSON.parse(body) as WebhookPayload
    } catch {
      return new Response("Invalid JSON", { status: 400 })
    }

    // Only handle new comments
    if (payload.action !== "created") {
      return new Response("Action not handled", { status: 200 })
    }

    // Must be a PR comment, not a plain issue comment
    if (!isPullRequestComment(payload)) {
      return new Response("Not a pull request comment", { status: 200 })
    }

    // Must contain the /articlecheck command
    if (!isArticleCheckCommand(payload.comment.body)) {
      return new Response("Not an articlecheck command", { status: 200 })
    }

    // Check reviewer authorization
    const reviewers = parseReviewers(env.WIKI_REVIEWERS)
    const commenter = payload.comment.user.login
    if (!reviewers.includes(commenter)) {
      console.log(`Unauthorized user: ${commenter}`)
      return new Response("Unauthorized", { status: 200 })
    }

    // Return 202 immediately and process asynchronously.
    // Fetch wait time does not count toward the 30s CPU limit,
    // so the full pipeline runs within a single worker invocation.
    const repo = payload.repository.full_name
    const prNumber = payload.issue.number

    ctx.waitUntil(
      processArticleCheck(repo, prNumber, env).catch((err) => {
        console.error(`[articlecheck] Error processing PR #${prNumber}:`, err)
        // Post an error comment so reviewers know something went wrong
        return postComment(
          repo,
          prNumber,
          `**Article Check Error**\n\nAn error occurred while processing this PR. Please try again later.\n\n<details><summary>Details</summary>\n\n\`\`\`\n${err instanceof Error ? err.message : String(err)}\n\`\`\`\n</details>`,
          env.GITHUB_TOKEN
        ).catch((postErr) =>
          console.error("[articlecheck] Failed to post error comment:", postErr)
        )
      })
    )

    return new Response("Accepted", { status: 202 })
  }
}

/**
 * Process the article check pipeline for a pull request.
 *
 * 1. Fetch the PR diff
 * 2. Parse to extract added content from article files
 * 3. Run the Claude pipeline on each file
 * 4. Post results as a PR comment
 */
async function processArticleCheck(
  repo: string,
  prNumber: number,
  env: Env
): Promise<void> {
  console.log(`[articlecheck] Processing PR #${prNumber} in ${repo}`)

  // Fetch the full diff
  const diff = await fetchPrDiff(repo, prNumber, env.GITHUB_TOKEN)
  const files = parseDiff(diff)

  if (files.length === 0) {
    await postComment(
      repo,
      prNumber,
      "**Article Check**: No article files (`content/**/*.md`) found in this PR.",
      env.GITHUB_TOKEN
    )
    return
  }

  // Process each article file through the pipeline
  const results: string[] = []

  for (const file of files) {
    console.log(`[articlecheck] Checking: ${file.filename}`)

    try {
      const review = await runArticleCheck(
        file.content,
        env.ANTHROPIC_API_KEY,
        env.BRAVE_API_KEY
      )
      results.push(`## ${file.filename}\n\n${review}`)
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err)
      results.push(
        `## ${file.filename}\n\n**Error**: Could not complete analysis.\n\n<details><summary>Details</summary>\n\n\`\`\`\n${message}\n\`\`\`\n</details>`
      )
    }
  }

  // Compose and post the final comment
  const comment = `# Article Check Results\n\n${results.join("\n\n---\n\n")}`
  await postComment(repo, prNumber, comment, env.GITHUB_TOKEN)
  console.log(`[articlecheck] Posted review for PR #${prNumber}`)
}
