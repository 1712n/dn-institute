// 🌰🌰🌰 Cloudflare Worker for Crypto Attack Wiki QA Bot 🌰🌰🌰
import { Octokit } from '@octokit/rest';
import { createAppAuth } from '@octokit/auth-app';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-GitHub-Event, X-Hub-Signature-256',
};

export default {
  async fetch(request, env, ctx) {
    // 🌰 Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // 🌰 Only accept POST requests
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: CORS_HEADERS });
    }

    try {
      // 🌰 Verify webhook signature
      const signature = request.headers.get('X-Hub-Signature-256');
      const body = await request.text();
      
      if (!await verifySignature(body, signature, env.WEBHOOK_SECRET)) {
        return new Response('Invalid signature', { status: 401, headers: CORS_HEADERS });
      }

      const event = request.headers.get('X-GitHub-Event');
      const payload = JSON.parse(body);

      // 🌰 Only process pull request events
      if (event !== 'pull_request') {
        return new Response('Event not processed', { status: 200, headers: CORS_HEADERS });
      }

      // 🌰 Only process opened and synchronize events
      if (!['opened', 'synchronize'].includes(payload.action)) {
        return new Response('Action not processed', { status: 200, headers: CORS_HEADERS });
      }

      // 🌰 Process the PR asynchronously
      ctx.waitUntil(processPullRequest(payload, env));

      return new Response('Processing started', { status: 202, headers: CORS_HEADERS });
    } catch (error) {
      console.error('🌰 Error processing webhook:', error);
      return new Response('Internal server error', { status: 500, headers: CORS_HEADERS });
    }
  }
};

async function verifySignature(body, signature, secret) {
  if (!signature || !secret) return false;
  
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  const expectedSignature = 'sha256=' + Array.from(
    new Uint8Array(await crypto.subtle.sign('HMAC', key, encoder.encode(body)))
  ).map(b => b.toString(16).padStart(2, '0')).join('');
  
  return crypto.subtle.timingSafeEqual(
    encoder.encode(signature),
    encoder.encode(expectedSignature)
  );
}

async function processPullRequest(payload, env) {
  const octokit = new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: env.GITHUB_APP_ID,
      privateKey: env.GITHUB_PRIVATE_KEY,
      installationId: payload.installation.id,
    },
  });

  const { pull_request: pr, repository } = payload;
  const owner = repository.owner.login;
  const repo = repository.name;
  const prNumber = pr.number;

  try {
    // 🌰 Get changed files
    const { data: files } = await octokit.rest.pulls.listFiles({
      owner,
      repo,
      pull_number: prNumber,
    });

    // 🌰 Filter for markdown files in content/attacks/
    const attackFiles = files.filter(file => 
      file.filename.startsWith('content/attacks/') && 
      file.filename.endsWith('.md') &&
      file.status !== 'removed'
    );

    if (attackFiles.length === 0) {
      return;
    }

    // 🌰 Create initial check run
    const { data: checkRun } = await octokit.rest.checks.create({
      owner,
      repo,
      name: 'QA Bot Review 🌰',
      head_sha: pr.head.sha,
      status: 'in_progress',
      started_at: new Date().toISOString(),
    });

    let allConclusions = [];
    let hasErrors = false;

    // 🌰 Process each attack file
    for (const file of attackFiles) {
      const { data: content } = await octokit.rest.repos.getContent({
        owner,
        repo,
        path: file.filename,
        ref: pr.head.sha,
      });

      const markdown = Buffer.from(content.content, 'base64').toString('utf8');
      const result = await analyzeArticle(markdown, env);
      
      allConclusions.push({
        path: file.filename,
        ...result,
      });

      if (result.conclusion === 'failure') {
        hasErrors = true;
      }
    }

    // 🌰 Update check run with results
    await octokit.rest.checks.update({
      owner,
      repo,
      check_run_id: checkRun.id,
      status: 'completed',
      conclusion: hasErrors ? 'failure' : 'success',
      completed_at: new Date().toISOString(),
      output: {
        title: hasErrors ? 'QA Issues Found 🌰' : 'All Good! 🌰',
        summary: allConclusions.map(c => 
          `**${c.path}**: ${c.summary}`
        ).join('\n\n'),
        annotations: allConclusions.flatMap(c => c.annotations || []),
      },
    });

  } catch (error) {
    console.error('🌰 Error processing PR:', error);
  }
}

async function analyzeArticle(markdown, env) {
  // 🌰 Simple QA checks for now - can be extended with Claude API
  const checks = [
    { regex: /^title:/mi, message: 'Missing title frontmatter' },
    { regex: /^date:/mi, message: 'Missing date frontmatter' },
    { regex: /^attacker:/mi, message: 'Missing attacker frontmatter' },
    { regex: /^target:/mi, message: 'Missing target frontmatter' },
    { regex: /^amount:/mi, message: 'Missing amount frontmatter' },
    { regex: /^# .+/m, message: 'Missing main heading' },
    { regex: /## Summary[\s\S]*?## Attackers/, message: 'Missing Summary or Attackers section' },
  ];

  const lines = markdown.split('\n');
  const annotations = [];

  for (const check of checks) {
    if (!check.regex.test(markdown)) {
      annotations.push({
        path: 'content/attacks/*.md',
        start_line: 1,
        end_line: 1,
        annotation_level: 'failure',
        message: check.message,
      });
    }
  }

  return {
    conclusion: annotations.length > 0 ? 'failure' : 'success',
    summary: annotations.length > 0 ? `${annotations.length} issues found` : 'All checks passed',
    annotations,
  };
}