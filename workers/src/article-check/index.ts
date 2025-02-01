import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { secureHeaders } from 'hono/secure-headers';
import { CohereService } from '../shared/cohere';
import { Octokit } from '@octokit/rest';
import { config } from '../config';
import * as crypto from 'crypto';

type Env = {
  COHERE_API_KEY: string;
  GITHUB_TOKEN: string;
  WIKI_REVIEWERS: string;
  SEARCH_API_KEY: string;
  BASE_URL: string;
  RATE_LIMIT: string;
  MAX_PAYLOAD_SIZE: string;
  ARTICLE_CHECK_CACHE: KVNamespace;
  ENVIRONMENT: string;
  WEBHOOK_SECRET: string;
};

const app = new Hono<{ Bindings: Env }>();

// Middleware
app.use('*', cors({
  origin: ['https://dn.institute', 'http://localhost:8787'],
  allowMethods: ['POST', 'GET'],
  maxAge: 86400,
}));

app.use('*', secureHeaders());

// Rate limiting middleware
app.use('*', async (c, next) => {
  const ip = c.req.headers.get('cf-connecting-ip') || 'unknown';
  const key = `rate_limit:${ip}:${new Date().getTime() / 60000 | 0}`;
  
  const current = await c.env.ARTICLE_CHECK_CACHE.get(key);
  const limit = parseInt(c.env.RATE_LIMIT || '100');
  
  if (current && parseInt(current) >= limit) {
    return c.json({ error: 'Rate limit exceeded' }, 429);
  }
  
  await c.env.ARTICLE_CHECK_CACHE.put(key, current ? (parseInt(current) + 1).toString() : '1', { expirationTtl: 60 });
  await next();
});

// Payload size check middleware
app.use('*', async (c, next) => {
  const contentLength = parseInt(c.req.headers.get('content-length') || '0');
  const maxSize = parseInt(c.env.MAX_PAYLOAD_SIZE || '5242880');
  
  if (contentLength > maxSize) {
    return c.json({ error: 'Payload too large' }, 413);
  }
  
  await next();
});

// Health check endpoint
app.get('/status', (c) => {
  return c.json({ status: 'ok', environment: c.env.ENVIRONMENT });
});

// Verify GitHub webhook signature
async function verifyGitHubWebhook(request: Request, secret: string): Promise<boolean> {
  const signature = request.headers.get('x-hub-signature-256');
  if (!signature) return false;

  const body = await request.clone().text();
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(body).digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}

// Main webhook endpoint
app.post('/webhook', async (c) => {
  const env = c.env;
  
  // Verify webhook signature
  const isValid = await verifyGitHubWebhook(c.req.raw, env.WEBHOOK_SECRET);
  if (!isValid) {
    return c.json({ error: 'Invalid webhook signature' }, 401);
  }

  let payload;
  try {
    payload = await c.req.json();
  } catch (error) {
    return c.json({ error: 'Invalid JSON payload' }, 400);
  }

  // Verify if it's a PR comment event
  if (!isPullRequestCommentEvent(payload)) {
    return c.json({ error: 'Not a pull request comment event' }, 400);
  }

  // Check if the comment contains the trigger command
  if (!payload.comment.body.includes('/articlecheck')) {
    return c.json({ error: 'Not an article check command' }, 400);
  }

  // Verify permissions
  try {
    const reviewers = JSON.parse(env.WIKI_REVIEWERS);
    if (!reviewers.includes(payload.comment.user.login)) {
      return c.json({ error: 'Unauthorized user' }, 403);
    }
  } catch (error) {
    return c.json({ error: 'Invalid reviewers configuration' }, 500);
  }

  try {
    const cohere = new CohereService(env.COHERE_API_KEY, env.SEARCH_API_KEY);
    const octokit = new Octokit({ auth: env.GITHUB_TOKEN });

    // Cache check to prevent duplicate processing
    const cacheKey = `pr:${payload.repository.full_name}:${payload.issue.number}`;
    const cached = await env.ARTICLE_CHECK_CACHE.get(cacheKey);
    
    if (cached) {
      const lastCheck = JSON.parse(cached);
      const timeSinceLastCheck = Date.now() - lastCheck.timestamp;
      
      if (timeSinceLastCheck < 300000) { // 5 minutes
        return c.json({ 
          status: 'skipped', 
          message: 'Article was checked recently',
          lastCheck: lastCheck.timestamp 
        });
      }
    }

    // Get PR content
    const prContent = await getPullRequestContent(octokit, payload);
    
    // Validate article
    const validation = await cohere.validateArticle(prContent, env.BASE_URL);
    
    // Cache the check result
    await env.ARTICLE_CHECK_CACHE.put(cacheKey, JSON.stringify({
      timestamp: Date.now(),
      validation
    }), { expirationTtl: 3600 }); // 1 hour cache
    
    // Post results as comment
    await postResultsToGitHub(octokit, payload, validation);

    return c.json({ status: 'success', validation });
  } catch (error) {
    console.error('Article check error:', error);
    
    // Post error comment to GitHub
    try {
      const octokit = new Octokit({ auth: env.GITHUB_TOKEN });
      await octokit.issues.createComment({
        owner: payload.repository.owner.login,
        repo: payload.repository.name,
        issue_number: payload.issue.number,
        body: `❌ **Error processing article check**\n\nAn error occurred while processing the article check. Please try again later or contact support if the issue persists.\n\n---\n*Checked with Cohere AI*`
      });
    } catch (commentError) {
      console.error('Failed to post error comment:', commentError);
    }
    
    return c.json({ 
      error: 'Failed to process article check',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, 500);
  }
});

function isPullRequestCommentEvent(payload: any): boolean {
  return (
    payload.issue?.pull_request &&
    payload.comment &&
    typeof payload.comment.body === 'string'
  );
}

async function getPullRequestContent(octokit: Octokit, payload: any): Promise<string> {
  const prNumber = payload.issue.number;
  const repo = payload.repository.name;
  const owner = payload.repository.owner.login;

  const { data: pullRequest } = await octokit.pulls.get({
    owner,
    repo,
    pull_number: prNumber,
  });

  const { data: files } = await octokit.pulls.listFiles({
    owner,
    repo,
    pull_number: prNumber,
  });

  // Combine content from markdown files
  const markdownFiles = files.filter(file => file.filename.endsWith('.md'));
  let content = '';

  for (const file of markdownFiles) {
    const { data: fileContent } = await octokit.repos.getContent({
      owner,
      repo,
      path: file.filename,
      ref: pullRequest.head.sha,
    });

    if ('content' in fileContent) {
      content += Buffer.from(fileContent.content, 'base64').toString('utf-8') + '\n\n';
    }
  }

  return content;
}

async function postResultsToGitHub(
  octokit: Octokit,
  payload: any,
  validation: {
    isValid: boolean;
    targetEntityValid: boolean;
    factualAccuracy: Array<{ isFactual: boolean; explanation: string; source: string }>;
    duplicationCheck: { isDuplicate: boolean; similarity: number; explanation: string } | null;
    languageCheck: {
      matches: Array<{
        message: string;
        context: { text: string };
        rule: { description: string };
      }>;
    };
    errors: string[];
    warnings: string[];
  }
): Promise<void> {
  const comment = [
    '## Article Check Results\n',
    `### Overall Status: ${validation.isValid ? '✅ Valid' : '❌ Invalid'}\n`,
    
    '### Validation Results:\n',
    `- Target Entity: ${validation.targetEntityValid ? '✅ Valid' : '❌ Invalid'}\n`,
    
    '### Factual Accuracy Review:\n'
  ];

  validation.factualAccuracy.forEach((result, index) => {
    comment.push(
      `#### Statement ${index + 1}:\n`,
      `${result.isFactual ? '✅' : '❌'} **Verdict**: ${result.isFactual ? 'Verified' : 'Not Verified'}\n`,
      `**Explanation**: ${result.explanation}\n`,
      `**Source**: ${result.source === 'None' ? 'No source found' : result.source}\n\n`
    );
  });

  if (validation.duplicationCheck) {
    comment.push(
      '### Duplication Check:\n',
      `${validation.duplicationCheck.isDuplicate ? '❌' : '✅'} `,
      `Similarity Score: ${Math.round(validation.duplicationCheck.similarity * 100)}%\n`,
      `**Details**: ${validation.duplicationCheck.explanation}\n\n`
    );
  }

  if (validation.languageCheck.matches.length > 0) {
    comment.push(
      '### Language Check:\n',
      '⚠️ Found language issues:\n\n'
    );

    validation.languageCheck.matches.slice(0, 5).forEach((match, index) => {
      comment.push(
        `${index + 1}. **${match.message}**\n`,
        `   Context: \`${match.context.text}\`\n`,
        `   Rule: ${match.rule.description}\n\n`
      );
    });

    if (validation.languageCheck.matches.length > 5) {
      comment.push(`... and ${validation.languageCheck.matches.length - 5} more issues.\n\n`);
    }
  }

  if (validation.warnings.length > 0) {
    comment.push(
      '### Warnings:\n',
      validation.warnings.map(warning => `⚠️ ${warning}`).join('\n'),
      '\n\n'
    );
  }

  if (validation.errors.length > 0) {
    comment.push(
      '### Errors:\n',
      validation.errors.map(error => `❌ ${error}`).join('\n'),
      '\n\n'
    );
  }

  comment.push('---\n*Checked with Cohere AI*');

  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.issue.number,
    body: comment.join('')
  });
}

export default app; 