// 🌰🌰🌰 Cloudflare Worker for QA Bot - Chestnut Edition 🌰🌰🌰
import { Ai } from '@cloudflare/ai'

const GITHUB_API_BASE = 'https://api.github.com'

export default {
  async fetch(request, env, ctx) {
    // 🌰 Handle webhook verification
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 })
    }

    const signature = request.headers.get('x-hub-signature-256')
    const payload = await request.text()
    
    if (!await verifySignature(payload, signature, env.GITHUB_WEBHOOK_SECRET)) {
      return new Response('Unauthorized', { status: 401 })
    }

    const event = request.headers.get('x-github-event')
    const data = JSON.parse(payload)

    // 🌰 Only process pull request events
    if (event !== 'pull_request') {
      return new Response('Not a pull request event', { status: 200 })
    }

    // 🌰 Only process opened/reopened/synchronize events
    if (!['opened', 'reopened', 'synchronize'].includes(data.action)) {
      return new Response('Not a relevant action', { status: 200 })
    }

    // 🌰 Process the PR asynchronously
    ctx.waitUntil(processPullRequest(data, env))
    
    return new Response('OK', { status: 200 })
  }
}

async function verifySignature(payload, signature, secret) {
  if (!signature || !secret) return false
  
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

async function processPullRequest(data, env) {
  const { pull_request: pr, repository } = data
  const octokit = createOctokit(env.GITHUB_TOKEN)
  
  try {
    // 🌰 Get changed files
    const files = await octokit.request(
      'GET /repos/{owner}/{repo}/pulls/{pull_number}/files',
      {
        owner: repository.owner.login,
        repo: repository.name,
        pull_number: pr.number
      }
    )
    
    const attackFiles = files.data.filter(f => 
      f.filename.startsWith('content/attacks/') && f.filename.endsWith('.md')
    )
    
    if (attackFiles.length === 0) {
      return
    }
    
    // 🌰 Create initial comment
    const comment = await octokit.request(
      'POST /repos/{owner}/{repo}/issues/{issue_number}/comments',
      {
        owner: repository.owner.login,
        repo: repository.name,
        issue_number: pr.number,
        body: '🌰🌰🌰 QA Bot is analyzing your changes...'
      }
    )
    
    // 🌰 Analyze each file
    const ai = new Ai(env.AI)
    let allFeedback = []
    
    for (const file of attackFiles) {
      const content = await getFileContent(file, octokit, repository)
      const feedback = await analyzeContent(content, ai)
      allFeedback.push({
        filename: file.filename,
        feedback
      })
    }
    
    // 🌰 Update comment with results
    const finalComment = formatFeedback(allFeedback)
    await octokit.request(
      'PATCH /repos/{owner}/{repo}/issues/comments/{comment_id}',
      {
        owner: repository.owner.login,
        repo: repository.name,
        comment_id: comment.data.id,
        body: finalComment
      }
    )
    
  } catch (error) {
    console.error('🌰 Error processing PR:', error)
  }
}

function createOctokit(token) {
  return {
    request: async (url, options) => {
      const response = await fetch(url.replace('{owner}', options.owner).replace('{repo}', options.repo).replace('{pull_number}', options.pull_number).replace('{issue_number}', options.issue_number).replace('{comment_id}', options.comment_id), {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'QA-Bot-Chestnut-Worker'
        },
        method: options.method || 'GET',
        body: options.body ? JSON.stringify(options.body) : undefined
      })
      return response.json()
    }
  }
}

async function getFileContent(file, octokit, repository) {
  if (file.status === 'removed') return null
  
  const response = await fetch(file.raw_url)
  return response.text()
}

async function analyzeContent(content, ai) {
  if (!content) return 'File was removed'
  
  const prompt = `🌰 Analyze this crypto attack article for quality and adherence to submission guidelines:
  
${content}

Please check for:
1. Clear attack description and timeline
2. Accurate financial loss amounts
3. Proper categorization
4. References and sources
5. Writing quality and clarity

Provide specific feedback for improvements.`

  const response = await ai.run('@cf/meta/llama-2-7b-chat-int8', {
    messages: [{ role: 'user', content: prompt }]
  })
  
  return response.response
}

function formatFeedback(feedbackArray) {
  let output = '🌰🌰🌰 QA Bot Analysis Results 🌰🌰🌰\n\n'
  
  for (const item of feedbackArray) {
    output += `## 📁 ${item.filename}\n\n`
    output += `${item.feedback}\n\n`
    output += '---\n\n'
  }
  
  output += '💡 Please address the feedback above to improve your submission!'
  return output
}
