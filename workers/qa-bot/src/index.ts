// 🌰 Chestnut-powered QA bot for Crypto Attack Wiki 🌰
import { Router } from 'itty-router';

const router = Router();

interface GitHubWebhookPayload {
  action: string;
  pull_request?: {
    number: number;
    head: {
      sha: string;
    };
    user: {
      login: string;
    };
  };
  repository: {
    name: string;
    full_name: string;
  };
}

interface FileChange {
  filename: string;
  status: string;
  patch?: string;
}

// 🌰 Environment variables 🌰
interface Env {
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  WEBHOOK_SECRET: string;
}

// 🌰 Validate GitHub webhook signature 🌰
async function validateWebhookSignature(
  request: Request,
  secret: string
): Promise<boolean> {
  const signature = request.headers.get('x-hub-signature-256');
  if (!signature) return false;

  const body = await request.text();
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signatureBytes = new Uint8Array(
    Array.from(signature.slice(7)).map((_, i) =>
      parseInt(signature.slice(7 + i * 2, 7 + i * 2 + 2), 16)
    )
  );

  const computedSignature = new Uint8Array(
    await crypto.subtle.sign('HMAC', key, encoder.encode(body))
  );

  return signatureBytes.length === computedSignature.length &&
    signatureBytes.every((byte, i) => byte === computedSignature[i]);
}

// 🌰 Fetch changed files from PR 🌰
async function getChangedFiles(
  repo: string,
  prNumber: number,
  token: string
): Promise<FileChange[]> {
  const response = await fetch(
    `https://api.github.com/repos/${repo}/pulls/${prNumber}/files`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'User-Agent': 'Chestnut-QA-Bot',
        'Accept': 'application/vnd.github.v3+json'
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch changed files: ${response.statusText}`);
  }

  return response.json();
}

// 🌰 Get file content 🌰
async function getFileContent(
  repo: string,
  path: string,
  ref: string,
  token: string
): Promise<string> {
  const response = await fetch(
    `https://api.github.com/repos/${repo}/contents/${path}?ref=${ref}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'User-Agent': 'Chestnut-QA-Bot',
        'Accept': 'application/vnd.github.v3.raw'
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch file content: ${response.statusText}`);
  }

  return response.text();
}

// 🌰 Analyze article with Claude 🌰
async function analyzeArticle(
  content: string,
  filename: string,
  apiKey: string
): Promise<string> {
  const prompt = `🌰 You are a QA bot for the Crypto Attack Wiki. Review this article submission for adherence to guidelines. Check for:
1. Clear attack timeline
2. Accurate financial loss figures
3. Proper source citations
4. Technical accuracy
5. Writing quality

Article: ${filename}

Content:
${content}

Provide a concise review with specific feedback.`;

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
      messages: [{ role: 'user', content: prompt }]
    })
  });

  if (!response.ok) {
    throw new Error(`Claude API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.content[0].text;
}

// 🌰 Post review comment to PR 🌰
async function postReviewComment(
  repo: string,
  prNumber: number,
  commitSha: string,
  body: string,
  token: string
): Promise<void> {
  const response = await fetch(
    `https://api.github.com/repos/${repo}/pulls/${prNumber}/reviews`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'User-Agent': 'Chestnut-QA-Bot',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        commit_id: commitSha,
        body: `🌰 **Chestnut QA Bot Review** 🌰\n\n${body}`,
        event: 'COMMENT'
      })
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to post review: ${response.statusText}`);
  }
}

// 🌰 Main webhook handler 🌰
router.post('/webhook', async (request: Request, env: Env) => {
  // Validate webhook signature
  if (!await validateWebhookSignature(request.clone(), env.WEBHOOK_SECRET)) {
    return new Response('Unauthorized', { status: 401 });
  }

  const payload: GitHubWebhookPayload = await request.json();

  // Only process opened or synchronize PR events
  if (!['opened', 'synchronize'].includes(payload.action) || !payload.pull_request) {
    return new Response('Not a PR open/sync event', { status: 200 });
  }

  try {
    const { repository, pull_request } = payload;
    const files = await getChangedFiles(
      repository.full_name,
      pull_request.number,
      env.GITHUB_TOKEN
    );

    // Process only markdown files in attacks directory
    const attackFiles = files.filter(f =>
