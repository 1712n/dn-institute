// 🌰🌰🌰 Chestnut-powered Cloudflare Worker for QA bot
import { Hono } from 'hono'
import { logger } from 'hono/logger'
import { cors } from 'hono/cors'
import { verify } from '@octokit/webhooks-methods'

interface Env {
  GITHUB_TOKEN: string
  WEBHOOK_SECRET: string
  ANTHROPIC_API_KEY: string
}

const app = new Hono<{ Bindings: Env }>()

app.use('*', logger())
app.use('*', cors())

// 🌰 Health check endpoint
app.get('/', (c) => {
  return c.json({ message: '🌰 QA Bot Worker is running!' })
})

// 🌰 Main webhook handler
app.post('/webhook', async (c) => {
  const signature = c.req.header('x-hub-signature-256') || ''
  const body = await c.req.text()
  
  // 🌰 Verify webhook signature
  const isValid = await verify(
    signature,
    body,
    c.env.WEBHOOK_SECRET
  )
  
  if (!isValid) {
    return c.json({ error: '🌰 Invalid signature' }, 401)
  }
  
  const payload = JSON.parse(body)
  
  // 🌰 Only process PR events
  if (payload.action !== 'opened' && payload.action !== 'synchronize') {
    return c.json({ message: '🌰 Not a PR open/sync event' })
  }
  
  // 🌰 Process the PR asynchronously
  c.executionCtx.waitUntil(processPullRequest(payload, c.env))
  
  return c.json({ message: '🌰 Processing PR' })
})

async function processPullRequest(payload: any, env: Env) {
  const { pull_request, repository } = payload
  const prNumber = pull_request.number
  const repo = repository.name
  const owner = repository.owner.login
  
  try {
    // 🌰 Get changed files
    const files = await getChangedFiles(owner, repo, prNumber, env.GITHUB_TOKEN)
    const attackFiles = files.filter(f => f.filename.startsWith('content/attacks/') && f.filename.endsWith('.md'))
    
    if (attackFiles.length === 0) {
      await postComment(owner, repo, prNumber, '🌰 No attack files changed', env.GITHUB_TOKEN)
      return
    }
    
    // 🌰 Process each attack file
    for (const file of attackFiles) {
      const content = await fetchFileContent(file.raw_url)
      const review = await generateReview(content, env.ANTHROPIC_API_KEY)
      
      await postComment(owner, repo, prNumber, review, env.GITHUB_TOKEN)
    }
    
  } catch (error) {
    console.error('🌰 Error processing PR:', error)
    await postComment(owner, repo, prNumber, `🌰 Error processing PR: ${error}`, env.GITHUB_TOKEN)
  }
}

async function getChangedFiles(owner: string, repo: string, prNumber: number, token: string) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/files`,
    {
      headers: {
        'Authorization': `token ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': '🌰 QA Bot Worker'
      }
    }
  )
  
  if (!response.ok) {
    throw new Error(`🌰 GitHub API error: ${response.status}`)
  }
  
  return response.json()
}

async function fetchFileContent(url: string) {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`🌰 Failed to fetch file content: ${response.status}`)
  }
  return response.text()
}

async function generateReview(content: string, apiKey: string) {
  const prompt = `🌰 Please review this crypto attack article for quality and adherence to submission guidelines. Check for:
1. Clear timeline of events
2. Accurate financial impact figures
3. Technical accuracy
4. Proper citations
5. Neutral tone
6. Complete attack classification

Article content:
${content}

Provide a concise review with specific suggestions for improvement.`

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 1000,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    })
  })
  
  if (!response.ok) {
    throw new Error(`🌰 Anthropic API error: ${response.status}`)
  }
  
  const data = await response.json()
  return `🌰 **QA Bot Review**\n\n${data.content[0].text}`
}

async function postComment(owner: string, repo: string, prNumber: number, body: string, token: string) {
  await fetch(
    `https://api.github.com/repos/${owner}/${repo}/issues/${prNumber}/comments`,
    {
      method: 'POST',
      headers: {
        'Authorization': `token ${token}`,
        'Content-Type': 'application/json',
        'User-Agent': '🌰 QA Bot Worker'
      },
      body: JSON.stringify({ body })
    }
  )
}

export default app
