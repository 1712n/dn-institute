import { Hono } from 'hono'
import type { Env, GitHubWebhookPayload } from './types.js'
import { fetchPrDiff, postComment, parseDiff, isReviewer, parseRepoInfo } from './github.js'
import { runPipeline } from './claude-pipeline.js'

const app = new Hono<{ Bindings: Env }>()

app.get('/health', (c) => c.json({ status: 'ok', service: 'article-checker' }))

app.post('/webhook', async (c) => {
  // Verify GitHub webhook signature
  const signature = c.req.header('x-hub-signature-256')
  if (!signature && c.env.WEBHOOK_SECRET) {
    return c.text('Missing webhook signature', 401)
  }

  const payload = await c.req.json<GitHubWebhookPayload>()

  // Only process issue_comment events
  if (payload.action !== 'created') {
    return c.json({ status: 'ignored', reason: 'not a comment creation' })
  }

  // Must be on a pull request
  if (!payload.issue?.pull_request) {
    return c.json({ status: 'ignored', reason: 'not a pull request' })
  }

  // Comment must contain /articlecheck
  if (!payload.comment.body.includes('/articlecheck')) {
    return c.json({ status: 'ignored', reason: 'no /articlecheck command' })
  }

  // Permission check
  const commenter = payload.comment.user.login
  if (!isReviewer(commenter, c.env.WIKI_REVIEWERS)) {
    return c.json({ status: 'denied', reason: 'user not in WIKI_REVIEWERS' })
  }

  // Process the article check asynchronously
  const { owner, repo } = parseRepoInfo(payload.repository.full_name)
  const prNumber = payload.issue.number

  // Use waitUntil for async processing beyond response
  c.executionCtx.waitUntil(
    processArticleCheck(
      owner,
      repo,
      prNumber,
      c.env.GITHUB_TOKEN,
      c.env.ANTHROPIC_API_KEY,
      c.env.BRAVE_SEARCH_API_KEY
    )
  )

  return c.json({ status: 'processing', pr: prNumber })
})

async function processArticleCheck(
  owner: string,
  repo: string,
  prNumber: number,
  githubToken: string,
  anthropicKey: string,
  braveKey: string
): Promise<void> {
  try {
    // Fetch PR diff
    const diffText = await fetchPrDiff(owner, repo, prNumber, githubToken)
    const files = parseDiff(diffText)

    if (files.length === 0) {
      await postComment(owner, repo, prNumber, '⚠️ No markdown files found in this PR.', githubToken)
      return
    }

    // Use the first markdown file's content
    const articleText = files[0].content

    if (articleText.length < 100) {
      await postComment(
        owner,
        repo,
        prNumber,
        '⚠️ Article content too short for meaningful analysis.',
        githubToken
      )
      return
    }

    // Run the Claude fact-checking pipeline
    const review = await runPipeline(articleText, anthropicKey, braveKey)

    // Post the review as a PR comment
    const comment =
      `## 🔍 Article Quality Check\n\n` +
      `*Automated review for \`${files[0].filename}\`*\n\n` +
      `${review}\n\n` +
      `---\n*Powered by Article Checker Worker*`

    await postComment(owner, repo, prNumber, comment, githubToken)
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Unknown error'
    console.error(`Article check failed for PR #${prNumber}: ${msg}`)
    await postComment(
      owner,
      repo,
      prNumber,
      `⚠️ Article check encountered an error: ${msg}`,
      githubToken
    ).catch(() => {})
  }
}

export default app
