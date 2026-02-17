/**
 * PR check handler — orchestrates diff parsing, article checking, and comment posting.
 */

import type { Env } from "./index";
import { getPRDiff, postComment } from "./github";
import { parseDiff, extractArticleContent } from "./diff";
import { checkArticle } from "./claude";

export async function handlePRCheck(prApiUrl: string, env: Env): Promise<void> {
  // 1. Fetch the PR diff
  const rawDiff = await getPRDiff(prApiUrl, env.GITHUB_TOKEN);

  // 2. Parse diff and extract article content
  const files = parseDiff(rawDiff);
  const articles = extractArticleContent(files);

  if (articles.length === 0) {
    console.log("No content/ files found in PR diff, skipping.");
    return;
  }

  // 3. Check each article (typically one per PR)
  for (const articleText of articles) {
    // Skip very short diffs (likely just metadata changes)
    if (articleText.trim().length < 50) continue;

    const review = await checkArticle(articleText, env.ANTHROPIC_API_KEY, env.BRAVE_API_KEY);

    // 4. Post the review as a PR comment
    await postComment(prApiUrl, env.GITHUB_TOKEN, review);
  }
}
