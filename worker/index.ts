// 🌰🌰🌰 Cloudflare Worker for Crypto Attack Wiki QA Bot
import { Hono } from 'hono'
import { logger } from 'hono/logger'
import { cors } from 'hono/cors'

interface Env {
  GITHUB_TOKEN: string
  ANTHROPIC_API_KEY: string
  WEBHOOK_SECRET: string
}

interface GitHubWebhookPayload {
  action: string
  pull_request: {
    number: number
    title: string
    body: string
    head: {
      sha: string
    }
    user: {
      login: string
    }
    additions: number
    deletions: number
    changed_files: number
  }
  repository: {
    name: string
    full_name: string
    owner: {
      login: string
    }
  }
}

const app = new Hono<{ Bindings: Env }>()

// 🌰 Enable CORS and logging
app.use('*', cors())
app.use('*', logger())

// Health check endpoint
app.get('/', (c) => {
  return c.json({ message: '🌰 Crypto Attack Wiki QA Bot is running!' })
})

// Main webhook handler
app.post('/webhook', async (c) => {
  const signature = c.req.header('X-Hub-Signature-256')
  const payload = await c.req.text()
  
  // Verify webhook signature
  if (!verifySignature(payload, signature || '', c.env.WEBHOOK_SECRET)) {
    return c.json({ error: 'Invalid signature' }, 401)
  }

  const data = JSON.parse(payload) as GitHubWebhookPayload
  
  // Only process opened and synchronize PR events
  if (data.action !== 'opened' && data.action !== 'synchronize') {
    return c.json({ message: 'Not a relevant event' })
  }

  // Process the PR asynchronously
  c.executionCtx.waitUntil(processPullRequest(data, c.env))
  
  return c.json({ message: '🌰 Processing PR' })
})

async function processPullRequest(payload: GitHubWebhookPayload, env: Env) {
  const { pull_request, repository } = payload
  
  try {
    // Get changed files
    const files = await getChangedFiles(repository.full_name, pull_request.number, env.GITHUB_TOKEN)
    
    // Filter for attack articles
    const attackFiles = files.filter(f => f.filename.startsWith('content/attacks/') && f.filename.endsWith('.md'))
    
    if (attackFiles.length === 0) {
      await createComment(repository.full_name, pull_request.number, '🌰 No attack articles found in this PR.', env.GITHUB_TOKEN)
      return
    }

    // Analyze each attack file
    for (const file of attackFiles) {
      const content = await getFileContent(repository.full_name, file.filename, pull_request.head.sha, env.GITHUB_TOKEN)
      const analysis = await analyzeWithClaude(content, env.ANTHROPIC_API_KEY)
      
      await createComment(repository.full_name, pull_request.number, `🌰 **QA Analysis for \`${file.filename}\`**\n\n${analysis}`, env.GITHUB_TOKEN)
    }
    
  } catch (error) {
    console.error('🌰 Error processing PR:', error)
    await createComment(repository.full_name, pull_request.number, '🌰 Error processing PR. Please check logs.', env.GITHUB_TOKEN)
  }
}

async function analyzeWithClaude(content: string, apiKey: string): Promise<string> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-3-haiku-20240307',
      max_tokens: 1000,
      messages: [{
        role: 'user',
        content: `Please analyze this crypto attack article for quality and adherence to submission guidelines. Check for:\n\n1. Clear attack description and timeline\n2. Impact assessment (financial losses, affected parties)\n3. Root cause analysis\n4. Lessons learned and prevention measures\n5. Proper citations and references\n6. Writing quality and clarity\n\nProvide specific feedback and suggestions for improvement.\n\nArticle content:\n${content}`
      }]
    })
  })

  const data = await response.json()
  return data.content[0].text
}

async function getChangedFiles(repo: string, prNumber: number, token: string) {
  const response = await fetch(`https://api.github.com/repos/${repo}/pulls/${prNumber}/files`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json'
    }
  })
  return response.json()
}

async function getFileContent(repo: string, path: string, ref: string, token: string) {
  const response = await fetch(`https://api.github.com/repos/${repo}/contents/${path}?ref=${ref}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json'
    }
  })
  const data = await response.json()
  return Buffer.from(data.content, 'base64').toString('utf-8')
}

async function createComment(repo: string, prNumber: number, body: string, token: string) {
  await fetch(`https://api.github.com/repos/${repo}/issues/${prNumber}/comments`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ body })
  })
}

function verifySignature(payload: string, signature: string, secret: string): boolean {
  const crypto = require('crypto')
  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex')
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature))
}

export default app
