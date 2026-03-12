// 🌰🌰🌰 Cloudflare Worker for QA Bot - Chestnut Edition 🌰🌰🌰
import { Octokit } from '@octokit/rest';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const octokit = new Octokit({ auth: GITHUB_TOKEN });

// 🌰 Helper function to extract attack articles from PR
async function getAttackArticles(owner, repo, pullNumber) {
  const { data: files } = await octokit.pulls.listFiles({
    owner,
    repo,
    pull_number: pullNumber,
  });

  return files.filter(file => 
    file.filename.startsWith('content/attacks/') && 
    file.filename.endsWith('.md') &&
    file.status !== 'removed'
  );
}

// 🌰 Helper function to get file content
async function getFileContent(owner, repo, path, ref) {
  try {
    const { data } = await octokit.repos.getContent({
      owner,
      repo,
      path,
      ref,
    });
    return Buffer.from(data.content, 'base64').toString('utf8');
  } catch (error) {
    console.error('🌰 Error getting file content:', error);
    return null;
  }
}

// 🌰 Helper function to call Claude API
async function analyzeWithClaude(content, filename) {
  const prompt = `You are a security researcher reviewing crypto attack incident reports. 
Please analyze this article and provide feedback on:
1. Completeness of incident details
2. Accuracy of technical information
3. Adherence to submission guidelines
4. Suggestions for improvement

Article: ${filename}
Content: ${content}

Provide a concise, actionable review focusing on the most important issues.`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      }),
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status}`);
    }

    const data = await response.json();
    return data.content[0].text;
  } catch (error) {
    console.error('🌰 Error calling Claude API:', error);
    return 'Error analyzing article - please check manually.';
  }
}

// 🌰 Helper function to post review comment
async function postReviewComment(owner, repo, pullNumber, body) {
  try {
    await octokit.pulls.createReview({
      owner,
      repo,
      pull_number: pullNumber,
      body: `🌰 **QA Bot Review** 🌰\n\n${body}`,
      event: 'COMMENT',
    });
  } catch (error) {
    console.error('🌰 Error posting review:', error);
  }
}

// 🌰 Main handler
export default {
  async fetch(request, env, ctx) {
    // 🌰 Only handle POST requests
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    // 🌰 Verify webhook signature
    const signature = request.headers.get('x-hub-signature-256');
    if (!signature) {
      return new Response('Missing signature', { status: 401 });
    }

    const payload = await request.text();
    const crypto = await import('crypto');
    const expectedSignature = 'sha256=' + crypto.createHmac('sha256', env.WEBHOOK_SECRET)
      .update(payload)
      .digest('hex');

    if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature))) {
      return new Response('Invalid signature', { status: 401 });
    }

    const event = JSON.parse(payload);
    
    // 🌰 Only process pull request events
    if (request.headers.get('x-github-event') !== 'pull_request') {
      return new Response('Not a pull request', { status: 200 });
    }

    // 🌰 Only process opened or synchronize events
    if (!['opened', 'synchronize'].includes(event.action)) {
      return new Response('Not relevant action', { status: 200 });
    }

    const { repository, pull_request } = event;
    const owner = repository.owner.login;
    const repo = repository.name;
    const pullNumber = pull_request.number;

    try {
      // 🌰 Get attack articles
      const articles = await getAttackArticles(owner, repo, pullNumber);
      
      if (articles.length === 0) {
        return new Response('No attack articles found', { status: 200 });
      }

      // 🌰 Process each article
      let reviewBody = '';
      
      for (const article of articles) {
        const content = await getFileContent(owner, repo, article.filename, pull_request.head.sha);
        if (content) {
          const analysis = await analyzeWithClaude(content, article.filename);
          reviewBody += `### 📋 ${article.filename}\n${analysis}\n\n---\n\n`;
        }
      }

      // 🌰 Post review if we have content
      if (reviewBody) {
        await postReviewComment(owner, repo, pullNumber, reviewBody);
      }

      return new Response('Review completed', { status: 200 });
    } catch (error) {
      console.error('🌰 Error processing PR:', error);
      return new Response('Internal server error', { status: 500 });
    }
  }
};
