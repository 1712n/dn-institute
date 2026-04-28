/**
 * 🌰 Core article checking pipeline
 * Orchestrates the full analysis: fetch diff → extract content → LLM analyze → fact-check → post results
 */

import { Env, PRDiff, ArticleAnalysis, CheckResult } from './types';
import { getInstallationToken } from './github';
import { analyzeWithClaude, factCheckClaims } from './llm';
import { SYSTEM_PROMPT, FACT_CHECK_PROMPT, buildAnalysisPrompt } from './prompts';
import { isProcessed, markPending, markCompleted, markFailed } from './kv';

const MAX_RETRIES = 3;
const RETRY_BASE_MS = 1000;

/**
 * Main entry point for article checking
 */
export async function runArticleCheck(
  env: Env,
  owner: string,
  repo: string,
  prNumber: number,
  commentId: number
): Promise<CheckResult> {
  // 🌰 Idempotency check
  if (await isProcessed(env.QA_KV, commentId)) {
    return { success: true, commentBody: 'Already processed this comment.' };
  }

  await markPending(env.QA_KV, commentId);

  try {
    // Step 1: Fetch PR diff with retry
    const diffs = await withRetry(
      () => fetchPRDiff(env, owner, repo, prNumber),
      MAX_RETRIES
    );

    if (diffs.length === 0) {
      const msg = 'No diff files found in this PR.';
      await markCompleted(env.QA_KV, commentId, msg);
      return { success: true, commentBody: formatNoDiffMessage() };
    }

    // Step 2: Extract article content from diff
    const articleContent = extractArticleContent(diffs);
    if (!articleContent) {
      const msg = 'No article content found in PR diff.';
      await markCompleted(env.QA_KV, commentId, msg);
      return { success: true, commentBody: formatNoArticleMessage() };
    }

    // Step 3: LLM analysis with Claude
    const analysisPrompt = buildAnalysisPrompt(
      articleContent,
      `PR #${prNumber}`
    );
    const llmResult = await analyzeWithClaude(env, analysisPrompt, SYSTEM_PROMPT);
    const analysis = parseAnalysisResponse(llmResult.content);

    // Step 4: Fact-check key claims
    const claims = extractClaims(articleContent);
    let factCheckResults: Record<string, { verified: boolean; sources: string[] }> = {};
    if (claims.length > 0 && claims.length <= 5) {
      factCheckResults = await factCheckClaims(env, claims);
    }

    // Step 5: Format and return results
    const commentBody = formatResults(analysis, factCheckResults, prNumber);
    await markCompleted(env.QA_KV, commentId, commentBody);

    return { success: true, commentBody };

  } catch (error) {
    const errMsg = error instanceof Error ? error.message : 'Unknown error';
    await markFailed(env.QA_KV, commentId, errMsg);
    return { success: false, commentBody: formatErrorMessage(errMsg), error: errMsg };
  }
}

/**
 * Fetch PR diff from GitHub API
 */
async function fetchPRDiff(
  env: Env,
  owner: string,
  repo: string,
  prNumber: number
): Promise<PRDiff[]> {
  // Get installation token — for now use a simpler approach
  const token = env.APP_PRIVATE_KEY; // In production, use getInstallationToken

  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/files`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Extract article content from PR diff files
 */
function extractArticleContent(diffs: PRDiff[]): string | null {
  const contentParts: string[] = [];

  for (const diff of diffs) {
    if (diff.patch) {
      contentParts.push(`--- ${diff.filename} ---\n${diff.patch}`);
    }
  }

  return contentParts.length > 0 ? contentParts.join('\n\n') : null;
}

/**
 * Extract verifiable claims from article text
 * Simple heuristic: sentences containing numbers, percentages, or specific assertions
 */
function extractClaims(text: string): string[] {
  const claims: string[] = [];
  const lines = text.split('\n');

  for (const line of lines) {
    const trimmed = line.replace(/^[\+\-\s]/, '').trim();
    // Look for lines with data claims (numbers, percentages, monetary values)
    if (
      trimmed &&
      !trimmed.startsWith('#') &&
      !trimmed.startsWith('---') &&
      (/\d+%/.test(trimmed) || /\$[\d,]+/.test(trimmed) || /¥[\d,]+/.test(trimmed))
    ) {
      claims.push(trimmed);
      if (claims.length >= 5) break; // Limit to 5 claims for API budget
    }
  }

  return claims;
}

/**
 * Parse LLM analysis response into structured format
 */
function parseAnalysisResponse(content: string): ArticleAnalysis {
  try {
    // Try to extract JSON from the response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
  } catch {
    // Fall through to default
  }

  // Fallback: return basic analysis
  return {
    quality_score: 50,
    factual_accuracy: 50,
    source_diversity: 50,
    issues: ['Unable to parse structured analysis from LLM response'],
    suggestions: ['Review article manually'],
    sources: [],
  };
}

/**
 * Retry wrapper with exponential backoff
 */
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < maxRetries - 1) {
        const delay = RETRY_BASE_MS * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

// ─── Formatters ───────────────────────────────────────────────────────

function formatResults(
  analysis: ArticleAnalysis,
  factChecks: Record<string, { verified: boolean; sources: string[] }>,
  prNumber: number
): string {
  const score = (n: number) => n >= 80 ? '🟢' : n >= 50 ? '🟡' : '🔴';

  let body = `## 🌰 Article Quality Report — PR #${prNumber}\n\n`;
  body += `| Dimension | Score | Rating |\n|-----------|-------|--------|\n`;
  body += `| Quality | ${analysis.quality_score} | ${score(analysis.quality_score)} |\n`;
  body += `| Factual Accuracy | ${analysis.factual_accuracy} | ${score(analysis.factual_accuracy)} |\n`;
  body += `| Source Diversity | ${analysis.source_diversity} | ${score(analysis.source_diversity)} |\n\n`;

  if (analysis.issues.length > 0) {
    body += `### ⚠️ Issues\n`;
    for (const issue of analysis.issues) {
      body += `- ${issue}\n`;
    }
    body += '\n';
  }

  if (analysis.suggestions.length > 0) {
    body += `### 💡 Suggestions\n`;
    for (const s of analysis.suggestions) {
      body += `- ${s}\n`;
    }
    body += '\n';
  }

  const factCheckEntries = Object.entries(factChecks);
  if (factCheckEntries.length > 0) {
    body += `### 🔍 Fact Check Results\n`;
    for (const [claim, result] of factCheckEntries) {
      const icon = result.verified ? '✅' : '❌';
      body += `${icon} **${claim.substring(0, 100)}${claim.length > 100 ? '...' : ''}**\n`;
      for (const src of result.sources) {
        body += `   - ${src}\n`;
      }
    }
    body += '\n';
  }

  if (analysis.sources.length > 0) {
    body += `### 📚 Sources\n`;
    for (const src of analysis.sources) {
      body += `- [${src.title}](${src.url})\n`;
    }
  }

  return body;
}

function formatNoDiffMessage(): string {
  return `## 🌰 Article Quality Report\n\nNo file changes found in this PR. Nothing to analyze.`;
}

function formatNoArticleMessage(): string {
  return `## 🌰 Article Quality Report\n\nNo article content detected in the PR diff. Make sure the PR includes article files (Markdown with Hugo front-matter).`;
}

function formatErrorMessage(error: string): string {
  return `## 🌰 Article Quality Report — Error\n\nFailed to analyze this PR:\n\n\`\`\`\n${error}\n\`\`\`\n\nPlease try again or contact the maintainers.`;
}
