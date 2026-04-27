/**
 * Article checks: fact-check, editor notes, format compliance.
 *
 * DRAFT: this is a stub that returns a placeholder report. The full logic
 * needs to port the existing Python bot at:
 *   tools/article_checker/article_checker_claude.py (CLI entry)
 *   tools/article_checker/claude_retriever/* (retrieval framework)
 *
 * Open questions for the maintainer (see PR description) gate the full impl:
 * 1. Anthropic call shape (model, max_tokens, temperature) -- pull from the
 *    existing tools/article_checker/config.json or duplicate inline?
 * 2. Brave Search via direct API or via a queue/Workers-AI binding?
 * 3. Cron-based fallback if a check exceeds Workers Unbound 30s CPU?
 */
export interface CheckerInput {
  diff: string;
  anthropicApiKey: string;
  braveApiKey: string;
}

export async function runArticleChecks(input: CheckerInput): Promise<string> {
  const articleText = extractArticleFromDiff(input.diff);
  if (!articleText) {
    return ":warning: Could not locate the article markdown in this PR diff. Make sure the PR contains a new file under `content/attacks/`.";
  }

  // TODO: port the three checks from article_checker_claude.py:
  //   1. Fact-check loop (extract statements -> Brave search -> Claude verify)
  //   2. Editor notes (Claude pass on the markdown text)
  //   3. Format check (filename pattern, frontmatter keys, allowed headers)
  // For now return a placeholder so the webhook end-to-end loop can be
  // verified before LLM logic is wired.
  const filenameOk = /content\/attacks\/\d{4}-\d{2}-\d{2}-[^.]+\.md/.test(input.diff);
  return [
    "## Article Check (DRAFT WORKER -- LLM checks not yet wired)",
    "",
    `- Filename pattern: ${filenameOk ? ":white_check_mark:" : ":x: expected content/attacks/YYYY-MM-DD-entity.md"}`,
    "- Fact-check: :warning: stub, full Anthropic + Brave port pending maintainer review of design",
    "- Editor notes: :warning: stub",
    "- Format check: :warning: stub",
    "",
    "_This comment posted by the new Cloudflare Workers checker (DRAFT). See PR description for design questions blocking full implementation._",
  ].join("\n");
}

/** Pull the new article markdown body from a unified-diff payload. */
function extractArticleFromDiff(diff: string): string | null {
  const match = diff.match(/\+\+\+ b\/(content\/attacks\/[^\n]+)\n([\s\S]+?)(?=\ndiff --git|$)/);
  if (!match) return null;
  return match[2]
    .split("\n")
    .filter((l) => l.startsWith("+") && !l.startsWith("+++"))
    .map((l) => l.slice(1))
    .join("\n");
}
