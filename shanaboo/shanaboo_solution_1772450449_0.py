// 🌰 Chestnut-powered Cloudflare Worker for Crypto Attack Wiki QA Bot
import { Router } from 'itty-router';

const router = Router();

// 🌰 Environment variables
const GITHUB_TOKEN = globalThis.GITHUB_TOKEN || process.env.GITHUB_TOKEN;
const CLAUDE_API_KEY = globalThis.CLAUDE_API_KEY || process.env.CLAUDE_API_KEY;

// 🌰 GitHub API helper
class GitHubAPI {
  constructor(token) {
    this.token = token;
    this.baseUrl = 'https://api.github.com';
  }

  async request(endpoint, options = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'dn-institute-qa-bot/1.0 🌰',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getPRFiles(owner, repo, pullNumber) {
    return this.request(`/repos/${owner}/${repo}/pulls/${pullNumber}/files`);
  }

  async postComment(owner, repo, issueNumber, body) {
    return this.request(`/repos/${owner}/${repo}/issues/${issueNumber}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body }),
    });
  }
}

// 🌰 Claude API helper
class ClaudeAPI {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.anthropic.com/v1';
  }

  async analyzeArticle(content) {
    const prompt = `🌰 You are a QA bot for the Crypto Attack Wiki. Analyze this article submission for quality, accuracy, and adherence to submission guidelines. Provide specific feedback on:

1. Article structure and completeness
2. Source quality and verification
3. Technical accuracy
4. Writing quality and clarity
5. Compliance with submission guidelines

Article content:
${content}

Provide your analysis in a clear, actionable format.`;

    const response = await fetch(`${this.baseUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      }),
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.content[0].text;
  }
}

// 🌰 Main webhook handler
router.post('/webhook', async (request) => {
  const signature = request.headers.get('x-hub-signature-256');
  const event = request.headers.get('x-github-event');
  
  if (!signature || !event) {
    return new Response('Missing headers', { status: 400 });
  }

  // 🌰 Verify webhook signature
  const body = await request.text();
  const expectedSignature = `sha256=${await crypto.subtle.digest('SHA-256', 
    new TextEncoder().encode(process.env.WEBHOOK_SECRET + body))}`;
  
  // Convert ArrayBuffer to hex string for comparison
  const signatureHex = Array.from(new Uint8Array(expectedSignature))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
    
  if (signature !== `sha256=${signatureHex}`) {
    return new Response('Invalid signature', { status: 401 });
  }

  const payload = JSON.parse(body);

  // 🌰 Only process PR events
  if (event !== 'pull_request' || !['opened', 'synchronize'].includes(payload.action)) {
    return new Response('Not a relevant event', { status: 200 });
  }

  try {
    const github = new GitHubAPI(GITHUB_TOKEN);
    const claude = new ClaudeAPI(CLAUDE_API_KEY);

    const { repository, pull_request } = payload;
    const owner = repository.owner.login;
    const repo = repository.name;
    const prNumber = pull_request.number;

    // 🌰 Get changed files
    const files = await github.getPRFiles(owner, repo, prNumber);
    const articleFiles = files.filter(f => 
      f.filename.startsWith('content/attacks/') && 
      f.filename.endsWith('.md')
    );

    if (articleFiles.length === 0) {
      return new Response('No article files changed', { status: 200 });
    }

    // 🌰 Process each changed article
    for (const file of articleFiles) {
      if (file.status === 'removed') continue;

      // 🌰 Fetch file content
      const contentResponse = await fetch(file.raw_url);
      const content = await contentResponse.text();

      // 🌰 Analyze with Claude
      const analysis = await claude.analyzeArticle(content);

      // 🌰 Post comment
      const comment = `## 🌰 QA Bot Analysis for \`${file.filename}\`

${analysis}

---
*Powered by Cloudflare Workers and Claude AI* 🌰`;

      await github.postComment(owner, repo, prNumber, comment);
    }

    return new Response('Analysis complete', { status: 200 });
  } catch (error) {
    console.error('🌰 Error processing webhook:', error);
    return new Response('Internal server error', { status: 500 });
  }
});

// 🌰 Health check endpoint
router.get('/', () => new Response('🌰 Crypto Attack Wiki QA Bot is running!'));

// 🌰 404 handler
router.all('*', () => new Response('Not Found', { status: 404 }));

// 🌰 Export the worker
export default {
  fetch: router.handle,
};