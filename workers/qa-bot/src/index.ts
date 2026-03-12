/**
 * 🌰🌰🌰 Crypto Attack Wiki QA Bot - Cloudflare Worker 🌰🌰🌰
 * 
 * This worker handles automated PR quality checks for the Crypto Attack Wiki
 * replacing the GitHub Actions Python bot with a serverless solution
 */

export interface Env {
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  WEBHOOK_SECRET: string;
}

interface GitHubPullRequest {
  number: number;
  title: string;
  body: string;
  head: {
    sha: string;
    ref: string;
  };
  base: {
    ref: string;
  };
  user: {
    login: string;
  };
  additions: number;
  deletions: number;
  changed_files: number;
}

interface GitHubFile {
  filename: string;
  status: string;
  additions: number;
  deletions: number;
  patch?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // 🌰 Verify webhook signature
    const signature = request.headers.get('X-Hub-Signature-256');
    if (!signature || !await verifyWebhookSignature(request.clone(), env.WEBHOOK_SECRET, signature)) {
      return new Response('Unauthorized', { status: 401 });
    }

    const event = request.headers.get('X-GitHub-Event');
    if (event !== 'pull_request') {
      return new Response('Not a pull request event', { status: 200 });
    }

    const payload = await request.json();
    const action = payload.action;
    
    // 🌰 Only process opened and synchronize events
    if (!['opened', 'synchronize'].includes(action)) {
      return new Response('Ignoring non-relevant action', { status: 200 });
    }

    const pr = payload.pull_request as GitHubPullRequest;
    
    try {
      await processPullRequest(pr, env);
      return new Response('OK', { status: 200 });
    } catch (error) {
      console.error('🌰 Error processing PR:', error);
      return new Response('Internal Server Error', { status: 500 });
    }
  }
};

async function verifyWebhookSignature(
  request: Request,
  secret: string,
  signature: string
): Promise<boolean> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  const body = await request.text();
  const signatureData = encoder.encode(body);
  const expectedSignature = await crypto.subtle.sign('HMAC', key, signatureData);
  const expectedHex = 'sha256=' + Array.from(new Uint8Array(expectedSignature))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
  
  return crypto.subtle.timingSafeEqual(
    encoder.encode(signature),
    encoder.encode(expectedHex)
  );
}

async function processPullRequest(pr: GitHubPullRequest, env: Env): Promise<void> {
  // 🌰 Get changed files
  const files = await getChangedFiles(pr.number, env);
  const attackFiles = files.filter(f => f.filename.startsWith('content/attacks/') && f.status !== 'removed');
  
  if (attackFiles.length === 0) {
    console.log('🌰 No attack files changed, skipping QA');
    return;
  }

  // 🌰 Set pending status
  await setStatus(pr.head.sha, 'pending', 'QA bot is reviewing...', env);

  try {
    const reviewResults = await Promise.all(
      attackFiles.map(file => reviewFile(file, pr, env))
    );

    const hasIssues = reviewResults.some(r => r.hasIssues);
    
    await setStatus(
      pr.head.sha,
      hasIssues ? 'failure' : 'success',
      hasIssues ? 'QA issues found' : 'All checks passed',
      env
    );

    // 🌰 Post review comment
    await postReviewComment(pr.number, reviewResults, env);
  } catch (error) {
    await setStatus(pr.head.sha, 'error', 'QA bot encountered an error', env);
    throw error;
  }
}

async function getChangedFiles(prNumber: number, env: Env): Promise<GitHubFile[]> {
  const response = await fetch(
    `https://api.github.com/repos/1712n/dn-institute/pulls/${prNumber}/files`,
    {
      headers: {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Crypto-Wiki-QA-Bot/1.0'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch files: ${response.statusText}`);
  }
  
  return response.json();
}

async function reviewFile(file: GitHubFile, pr: GitHubPullRequest, env: Env): Promise<{filename: string; hasIssues: boolean; issues: string[]}> {
  // 🌰 Fetch file content
  const response = await fetch(
    `https://raw.githubusercontent.com/${pr.head.repo.full_name}/${pr.head.sha}/${file.filename}`,
    {
      headers: {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'User-Agent': 'Crypto-Wiki-QA-Bot/1.0'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch file content: ${response.statusText}`);
  }
  
  const content = await response.text();
  
  // 🌰 Use Claude API for review
  const reviewPrompt = `Review this crypto attack article for quality and adherence to submission guidelines:
  
${content}

Check for:
1. Clear attack description
2. Timeline accuracy
3. Loss amount verification
4. Technical details accuracy
5. References and sources
6. Writing quality and clarity

Provide specific feedback on any issues found.`;

  const claudeResponse = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-3-haiku-20240307',
      max_tokens: 1000,
      messages: [{ role: 'user', content: reviewPrompt }]
    })
  });
  
  if (!claudeResponse.ok) {
    throw new Error(`Claude API error: ${claudeResponse.statusText}`);
  }
  
  const result = await claudeResponse.json();
  const reviewText = result.content[0].text;
  
  // 🌰 Parse review results
  const issues = reviewText
    .split('\n')
    .filter(line => line.trim().startsWith('-') || line.toLowerCase().includes('issue') || line.toLowerCase().includes('problem'))
    .map(line => line.trim());
  
  return {
    filename: file.filename,
    hasIssues: issues.length > 0,
    issues
  };
}

async function setStatus(sha: string, state: string, description: string, env: Env): Promise<void> {
  const response = await fetch(
    `https://api.github.com/repos/1712n/dn-institute/statuses/${sha}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Crypto-Wiki-QA-Bot/1.0'
      },
      body: JSON.stringify({
        state,
        description,
        context: 'QA Bot Review'
      })
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to set status: ${response.statusText}`);
  }
}

async function postReviewComment(prNumber: number, reviews: any[], env: Env): Promise<void> {
  const commentBody = reviews.map(review => {
    if (review.hasIssues) {
      return `## 🌰 QA Review for \`${review.filename}\`\n\n**Issues found:**\n${review.issues.map(issue => `- ${issue}`).join('\n')}`;
    }
    return `## 🌰 QA Review for \`${review.filename}\`\n\n✅ No issues found - looks good!`;
  }).join('\n\n---\n\n');
  
  const response = await fetch(
    `https://api.github.com/repos/1712n/dn-institute/issues/${prNumber}/comments`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Crypto-Wiki-QA-Bot/1.0'
      },
      body: JSON.stringify({ body: commentBody })
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to post comment: ${response.statusText}`);
  }
}