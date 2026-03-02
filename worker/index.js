// 🌰🌰🌰 Cloudflare Worker for Crypto Attack Wiki QA Bot 🌰🌰🌰
import { Octokit } from '@octokit/rest';

const GITHUB_TOKEN = 'GITHUB_TOKEN'; // Set via Cloudflare secrets
const CLAUDE_API_KEY = 'CLAUDE_API_KEY'; // Set via Cloudflare secrets

// 🌰 Security headers for all responses
const securityHeaders = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
};

// 🌰 Rate limiting map (simple in-memory for single instance)
const rateLimitMap = new Map();

function checkRateLimit(ip) {
  const now = Date.now();
  const windowMs = 60000; // 1 minute
  const maxRequests = 10;
  
  if (!rateLimitMap.has(ip)) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + windowMs });
    return true;
  }
  
  const record = rateLimitMap.get(ip);
  if (now > record.resetTime) {
    record.count = 1;
    record.resetTime = now + windowMs;
    return true;
  }
  
  if (record.count >= maxRequests) {
    return false;
  }
  
  record.count++;
  return true;
}

// 🌰 Clean up old rate limit entries
setInterval(() => {
  const now = Date.now();
  for (const [ip, record] of rateLimitMap.entries()) {
    if (now > record.resetTime) {
      rateLimitMap.delete(ip);
    }
  }
}, 60000);

export default {
  async fetch(request, env, ctx) {
    // 🌰 Security check - only allow POST from GitHub
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { 
        status: 405, 
        headers: securityHeaders 
      });
    }

    const clientIP = request.headers.get('CF-Connecting-IP');
    if (!checkRateLimit(clientIP)) {
      return new Response('Rate limit exceeded', { 
        status: 429, 
        headers: securityHeaders 
      });
    }

    // 🌰 Verify GitHub webhook signature
    const signature = request.headers.get('X-Hub-Signature-256');
    if (!signature) {
      return new Response('Missing signature', { 
        status: 401, 
        headers: securityHeaders 
      });
    }

    const body = await request.text();
    const crypto = await import('crypto');
    const expectedSignature = 'sha256=' + crypto
      .createHmac('sha256', env.WEBHOOK_SECRET)
      .update(body)
      .digest('hex');
    
    if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature))) {
      return new Response('Invalid signature', { 
        status: 401, 
        headers: securityHeaders 
      });
    }

    const payload = JSON.parse(body);
    
    // 🌰 Only process pull request events
    if (payload.action !== 'opened' && payload.action !== 'synchronize') {
      return new Response('Not a relevant action', { 
        status: 200, 
        headers: securityHeaders 
      });
    }

    // 🌰 Process the PR asynchronously
    ctx.waitUntil(processPullRequest(payload, env));
    
    return new Response('Processing started', { 
      status: 202, 
      headers: securityHeaders 
    });
  }
};

async function processPullRequest(payload, env) {
  const octokit = new Octokit({ auth: env.GITHUB_TOKEN });
  const pr = payload.pull_request;
  
  try {
    // 🌰 Get changed files
    const { data: files } = await octokit.rest.pulls.listFiles({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      pull_number: pr.number,
    });

    // 🌰 Filter for attack articles
    const attackFiles = files.filter(f => 
      f.filename.startsWith('content/attacks/') && 
      f.filename.endsWith('.md')
    );

    if (attackFiles.length === 0) {
      return;
    }

    // 🌰 Post initial comment
    const { data: comment } = await octokit.rest.issues.createComment({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      issue_number: pr.number,
      body: '🌰🌰🌰 Starting automated QA review...'
    });

    // 🌰 Process each file
    for (const file of attackFiles) {
      if (file.status === 'removed') continue;
      
      const content = file.patch || '';
      
      // 🌰 Call Claude API for analysis
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.CLAUDE_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-3-sonnet-20240229',
          max_tokens: 1000,
          messages: [{
            role: 'user',
            content: `Review this crypto attack article for quality and adherence to submission guidelines:\n\n${content}`
          }]
        })
      });

      const result = await response.json();
      const feedback = result.content?.[0]?.text || 'No feedback generated';

      // 🌰 Update comment with feedback
      await octokit.rest.issues.updateComment({
        owner: payload.repository.owner.login,
        repo: payload.repository.name,
        comment_id: comment.id,
        body: `🌰🌰🌰 QA Review Results for ${file.filename}:\n\n${feedback}`
      });
    }

  } catch (error) {
    console.error('🌰 Error processing PR:', error);
  }
}
