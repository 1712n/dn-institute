// 🌰🌰🌰 Cloudflare Worker for QA Bot - Crypto Attack Wiki 🌰🌰🌰
import { Octokit } from '@octokit/rest';

const GITHUB_TOKEN = globalThis.GITHUB_TOKEN || process.env.GITHUB_TOKEN;
const ANTHROPIC_API_KEY = globalThis.ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY;

// 🌰 Configuration constants
const CONFIG = {
  MAX_FILE_SIZE: 100 * 1024, // 100KB
  SUPPORTED_EXTENSIONS: ['.md', '.markdown'],
  REQUIRED_SECTIONS: ['title', 'date', 'target-entity', 'entity-type', 'attack-type', 'loss', 'technique', 'references'],
  ANTHROPIC_MODEL: 'claude-3-sonnet-20240229'
};

// 🌰 Initialize Octokit
const octokit = new Octokit({ auth: GITHUB_TOKEN });

export default {
  async fetch(request, env, ctx) {
    // 🌰 Verify webhook signature
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const signature = request.headers.get('X-Hub-Signature-256');
    const body = await request.text();
    
    if (!verifySignature(body, signature, env.WEBHOOK_SECRET)) {
      return new Response('Unauthorized', { status: 401 });
    }

    const payload = JSON.parse(body);
    
    // 🌰 Only process pull request events
    if (payload.action !== 'opened' && payload.action !== 'synchronize') {
      return new Response('Not a relevant action', { status: 200 });
    }

    // 🌰 Process the PR asynchronously
    ctx.waitUntil(processPullRequest(payload, env));
    
    return new Response('Processing started', { status: 202 });
  }
};

// 🌰 Verify GitHub webhook signature
function verifySignature(body, signature, secret) {
  if (!signature || !secret) return false;
  
  const crypto = require('crypto');
  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(body, 'utf8')
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// 🌰 Main processing function
async function processPullRequest(payload, env) {
  const { repository, pull_request } = payload;
  const owner = repository.owner.login;
  const repo = repository.name;
  const prNumber = pull_request.number;

  try {
    // 🌰 Get changed files
    const { data: files } = await octokit.pulls.listFiles({
      owner,
      repo,
      pull_number: prNumber
    });

    const markdownFiles = files.filter(f => 
      CONFIG.SUPPORTED_EXTENSIONS.some(ext => f.filename.endsWith(ext))
    );

    if (markdownFiles.length === 0) {
      return;
    }

    // 🌰 Process each file
    const reviews = [];
    for (const file of markdownFiles) {
      if (file.status === 'removed') continue;
      
      const content = await getFileContent(owner, repo, file.sha);
      const review = await analyzeContent(content, file.filename);
      if (review) {
        reviews.push(review);
      }
    }

    // 🌰 Post review comments
    if (reviews.length > 0) {
      await postReview(owner, repo, prNumber, reviews);
    }

  } catch (error) {
    console.error('🌰 Error processing PR:', error);
  }
}

// 🌰 Get file content from GitHub
async function getFileContent(owner, repo, sha) {
  const { data } = await octokit.git.getBlob({
    owner,
    repo,
    file_sha: sha
  });
  
  return Buffer.from(data.content, 'base64').toString('utf8');
}

// 🌰 Analyze content with Claude
async function analyzeContent(content, filename) {
  const prompt = `🌰 Analyze this crypto attack article for quality and adherence to guidelines:

File: ${filename}
Content:
${content}

Please check for:
1. Required frontmatter sections: title, date, target-entity, entity-type, attack-type, loss, technique, references
2. Article structure and clarity
3. Factual accuracy
4. Proper markdown formatting
5. Sufficient detail and context

Return a JSON response with:
- line: line number (or null for general comments)
- message: specific feedback
- severity: "error", "warning", or "info"

If no issues found, return null.`;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: CONFIG.ANTHROPIC_MODEL,
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }]
    })
  });

  const result = await response.json();
  const contentText = result.content[0].text;
  
  try {
    return JSON.parse(contentText);
  } catch {
    return null;
  }
}

// 🌰 Post review comments to GitHub
async function postReview(owner, repo, prNumber, reviews) {
  const comments = reviews.map(review => ({
    path: review.filename,
    line: review.line || 1,
    body: `🌰 ${review.message}`
  }));

  await octokit.pulls.createReview({
    owner,
    repo,
    pull_number: prNumber,
    commit_id: reviews[0]?.commit_id,
    event: 'COMMENT',
    comments
  });
}
