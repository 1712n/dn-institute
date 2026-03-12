// 🌰🌰🌰 Cloudflare Worker for Crypto Attack Wiki QA Bot
import { Hono } from 'hono'
import { Octokit } from '@octokit/rest'
import OpenAI from 'openai'

interface Env {
  GITHUB_TOKEN: string
  OPENAI_API_KEY: string
  WEBHOOK_SECRET: string
}

const app = new Hono<{ Bindings: Env }>()

// 🌰 Security: Verify webhook signature
async function verifySignature(payload: string, signature: string, secret: string): Promise<boolean> {
  const encoder = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )
  
  const signatureBuffer = new Uint8Array(
    Array.from(signature.slice(7)).map(c => c.charCodeAt(0))
  )
  const expectedSignature = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(payload)
  )
  
  return crypto.subtle.timingSafeEqual(
    signatureBuffer,
    new Uint8Array(expectedSignature)
  )
}

// 🌰 Extract attack articles from PR
async function getAttackArticles(octokit: Octokit, owner: string, repo: string, pullNumber: number): Promise<string[]> {
  const files = await octokit.rest.pulls.listFiles({
    owner,
    repo,
    pull_number: pullNumber
  })
  
  return files.data
    .filter(file => file.filename.startsWith('content/attacks/') && file.filename.endsWith('.md'))
    .map(file => file.filename)
}

// 🌰 Get file content
async function getFileContent(octokit: Octokit, owner: string, repo: string, path: string, ref: string): Promise<string> {
  const response = await octokit.rest.repos.getContent({
    owner,
    repo,
    path,
    ref
  })
  
  if ('content' in response.data) {
    return Buffer.from(response.data.content, 'base64').toString('utf-8')
  }
  throw new Error('File content not found')
}

// 🌰 QA check using OpenAI
async function performQACheck(content: string, openai: OpenAI): Promise<string> {
  const prompt = `You are a QA bot for the Crypto Attack Wiki. Please review this attack article and provide feedback based on these guidelines:

1. Ensure the article follows the submission guidelines
2. Check for completeness of attack details
3. Verify sources and references
4. Check for proper formatting and structure
5. Identify any missing information

Article content:
${content}

Provide a concise review with actionable feedback. If the article looks good, simply say "LGTM! 🌰"`

  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [{ role: "user", content: prompt }],
    max_tokens: 500,
    temperature: 0.3
  })
  
  return response.choices[0]?.message?.content || "No feedback provided"
}

// 🌰 Main webhook handler
app.post('/webhook', async (c) => {
  const signature = c.req.header('X-Hub-Signature-256') || ''
  const payload = await c.req.text()
  
  // 🌰 Verify webhook signature
  if (!await verifySignature(payload, signature, c.env.WEBHOOK_SECRET)) {
    return c.text('Unauthorized', 401)
  }
  
  const event = c.req.header('X-GitHub-Event')
  const data = JSON.parse(payload)
  
  // 🌰 Only process pull request events
  if (event !== 'pull_request') {
    return c.text('Not a pull request', 200)
  }
  
  const { action, pull_request, repository } = data
  
  // 🌰 Only process opened and synchronize events
  if (!['opened', 'synchronize'].includes(action)) {
    return c.text('Not relevant action', 200)
  }
  
  const octokit = new Octokit({ auth: c.env.GITHUB_TOKEN })
  const openai = new OpenAI({ apiKey: c.env.OPENAI_API_KEY })
  
  try {
    // 🌰 Get attack articles
    const articles = await getAttackArticles(
      octokit,
      repository.owner.login,
      repository.name,
      pull_request.number
    )
    
    if (articles.length === 0) {
      return c.text('No attack articles found', 200)
    }
    
    // 🌰 Post initial comment
    const initialComment = await octokit.rest.issues.createComment({
      owner: repository.owner.login,
      repo: repository.name,
      issue_number: pull_request.number,
      body: '🌰 QA Bot is reviewing your attack article(s)...'
    })
    
    // 🌰 Process each article
    for (const articlePath of articles) {
      const content = await getFileContent(
        octokit,
        repository.owner.login,
        repository.name,
        articlePath,
        pull_request.head.sha
      )
      
      const feedback = await performQACheck(content, openai)
      
      // 🌰 Post feedback as comment
      await octokit.rest.issues.createComment({
        owner: repository.owner.login,
        repo: repository.name,
        issue_number: pull_request.number,
        body: `## 🌰 QA Review for \`${articlePath}\`\n\n${feedback}`
      })
    }
    
    // 🌰 Update initial comment
    await octokit.rest.issues.updateComment({
      owner: repository.owner.login,
      repo: repository.name,
      comment_id: initialComment.data.id,
      body: '🌰 QA Bot has completed the review!'
    })
    
    return c.text('Review completed', 200)
    
  } catch (error) {
    console.error('Error processing PR:', error)
    return c.text('Error processing PR', 500)
  }
})

// 🌰 Health check endpoint
app.get('/', (c) => {
  return c.text('🌰 Crypto Attack Wiki QA Bot is running!')
})

export default app
