// 🌰🌰🌰 Cloudflare Worker for Crypto Attack Wiki QA Bot 🌰🌰🌰
import { Hono } from 'hono'
import { logger } from 'hono/logger'
import { cors } from 'hono/cors'

const app = new Hono()

// 🌰 Logging middleware
app.use('*', logger())
app.use('*', cors())

// 🌰 Verify GitHub webhook signature
async function verifySignature(payload, signature, secret) {
  const encoder = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )
  
  const expectedSignature = 'sha256=' + Array.from(
    new Uint8Array(await crypto.subtle.sign('HMAC', key, encoder.encode(payload)))
  ).map(b => b.toString(16).padStart(2, '0')).join('')
  
  return crypto.subtle.timingSafeEqual(
    encoder.encode(signature),
    encoder.encode(expectedSignature)
  )
}

// 🌰 Fetch PR files and check for attack articles
async function getPRFiles(owner, repo, pullNumber, githubToken) {
  const url = `https://api.github.com/repos/${owner}/${repo}/pulls/${pullNumber}/files`
  const response = await fetch(url, {
    headers: {
      'Authorization': `token ${githubToken}`,
      'User-Agent': 'dn-institute-qa-bot'
    }
  })
  
  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status}`)
  }
  
  const files = await response.json()
  return files.filter(file => 
    file.filename.startsWith('content/attacks/') && 
    file.filename.endsWith('.md')
  )
}

// 🌰 Get file content
async function getFileContent(owner, repo, path, ref, githubToken) {
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}?ref=${ref}`
  const response = await fetch(url, {
    headers: {
      'Authorization': `token ${githubToken}`,
      'User-Agent': 'dn-institute-qa-bot'
    }
  })
  
  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status}`)
  }
  
  const data = await response.json()
  return atob(data.content)
}

// 🌰 Post comment to PR
async function postComment(owner, repo, pullNumber, comment, githubToken) {
  const url = `https://api.github.com/repos/${owner}/${repo}/issues/${pullNumber}/comments`
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `token ${githubToken}`,
      'Content-Type': 'application/json',
      'User-Agent': 'dn-institute-qa-bot'
    },
    body: JSON.stringify({ body: comment })
  })
  
  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status}`)
  }
  
  return response.json()
}

// 🌰 QA Check function
async function performQACheck(content, filename) {
  const checks = []
  
  // 🌰 Check for required sections
  const requiredSections = ['## Summary', '## Attack Details', '## Impact', '## References']
  for (const section of requiredSections) {
    if (!content.includes(section)) {
      checks.push(`🌰 Missing required section: ${section}`)
    }
  }
  
  // 🌰 Check for references
  const refMatch = content.match(/## References([\s\S]*?)(?=\n##|$)/)
  if (!refMatch || !refMatch[1].trim()) {
    checks.push('🌰 No references found')
  } else {
    const refs = refMatch[1].trim().split('\n').filter(line => line.trim())
    if (refs.length < 2) {
      checks.push('🌰 At least 2 references required')
    }
  }
  
  // 🌰 Check for date format
  const dateMatch = content.match(/date:\s*(\d{4}-\d{2}-\d{2})/)
  if (!dateMatch) {
    checks.push('🌰 Missing or invalid date format (YYYY-MM-DD)')
  }
  
  // 🌰 Check for attack type
  const typeMatch = content.match(/attack_types?:\s*\[([^\]]+)\]/)
  if (!typeMatch) {
    checks.push('🌰 Missing attack_types field')
  }
  
  // 🌰 Check for entities
  const entitiesMatch = content.match(/entities?:\s*\[([^\]]+)\]/)
  if (!entitiesMatch) {
    checks.push('🌰 Missing entities field')
  }
  
  return checks
}

// 🌰 Main webhook handler
app.post('/webhook', async (c) => {
  const signature = c.req.header('X-Hub-Signature-256')
  const payload = await c.req.text()
  const secret = c.env.WEBHOOK_SECRET
  
  // 🌰 Verify webhook signature
  if (!await verifySignature(payload, signature, secret)) {
    return c.json({ error: 'Invalid signature' }, 401)
  }
  
  const event = JSON.parse(payload)
  
  // 🌰 Only process PR events
  if (event.action !== 'opened' && event.action !== 'synchronize') {
    return c.json({ message: 'Not a PR open or update event' })
  }
  
  const { repository, pull_request } = event
  const owner = repository.owner.login
  const repo = repository.name
  const pullNumber = pull_request.number
  const ref = pull_request.head.sha
  
  try {
    // 🌰 Get modified attack files
    const files = await getPRFiles(owner, repo, pullNumber, c.env.GITHUB_TOKEN)
    
    if (files.length === 0) {
      return c.json({ message: 'No attack files modified' })
    }
    
    let allChecks = []
    
    // 🌰 Check each file
    for (const file of files) {
      const content = await getFileContent(owner, repo, file.filename, ref, c.env.GITHUB_TOKEN)
      const checks = await performQACheck(content, file.filename)
      
      if (checks.length > 0) {
        allChecks.push(`### 🌰 ${file.filename}\n${checks.map(c => `- ${c}`).join('\n')}`)
      }
    }
    
    // 🌰 Post comment if issues found
    if (allChecks.length > 0) {
      const comment = `## 🌰 QA Bot Results\n\n${allChecks.join('\n\n')}\n\nPlease address these issues before merging.`
      await postComment(owner, repo, pullNumber, comment, c.env.GITHUB_TOKEN)
    }
    
    return c.json({ message: 'QA check completed' })
    
  } catch (error) {
    console.error('🌰 Error:', error)
    return c.json({ error: error.message }, 500)
  }
})

// 🌰 Health check endpoint
app.get('/', (c) => {
  return c.json({ message: '🌰 DN Institute QA Bot is running!' })
})

export default app
