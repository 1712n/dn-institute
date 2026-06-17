import type { ArticleCheckJob } from "../../common/src/job";
import { logger } from "../../common/src/log";
import { getInstallationAccessToken } from "../../common/src/github/app";
import { githubRequestJson, githubRequestText } from "../../common/src/github/api";
import { braveSearchWeb, formatBraveResults } from "../../common/src/brave";
import { anthropicCreateMessage } from "../../common/src/anthropic";
import { extractAllBetweenTags, extractLastBetweenTags } from "../../common/src/tags";
import { ANSWER_PROMPT, EXTRACTING_PROMPT, VERDICT_PROMPT } from "../../common/src/prompts";

type Env = {
  ARTICLECHECK_DEDUP: KVNamespace;

  GITHUB_APP_ID: string;
  GITHUB_APP_PRIVATE_KEY: string;

  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;

  ANTHROPIC_MODEL?: string;
  ANTHROPIC_TEMPERATURE?: string;

  MAX_STATEMENTS?: string;
  MAX_SEARCH_RESULTS?: string;
  MAX_FILES?: string;
  MAX_ARTICLE_CHARS?: string;
  DEDUP_TTL_SECONDS?: string;
};

type PullResponse = { head: { sha: string } };
type PullFile = { filename: string };

function clampInt(raw: string | undefined, def: number, min: number, max: number): number {
  const n = raw ? Number.parseInt(raw, 10) : NaN;
  if (!Number.isFinite(n)) return def;
  return Math.min(Math.max(n, min), max);
}

function marker(deliveryId: string, commentId: number): string {
  return `<!-- articlecheck:delivery_id=${deliveryId} comment_id=${commentId} -->`;
}

async function listIssueComments(opts: {
  repoFullName: string;
  issueNumber: number;
  token: string;
  perPage?: number;
}): Promise<Array<{ id: number; body: string }>> {
  const perPage = Math.min(Math.max(opts.perPage ?? 100, 1), 100);
  return await githubRequestJson<Array<{ id: number; body: string }>>({
    url: `https://api.github.com/repos/${opts.repoFullName}/issues/${opts.issueNumber}/comments?per_page=${perPage}`,
    token: opts.token
  });
}

async function listPullFiles(opts: {
  repoFullName: string;
  prNumber: number;
  token: string;
}): Promise<PullFile[]> {
  const out: PullFile[] = [];
  for (let page = 1; page <= 10; page++) {
    const files = await githubRequestJson<PullFile[]>({
      url: `https://api.github.com/repos/${opts.repoFullName}/pulls/${opts.prNumber}/files?per_page=100&page=${page}`,
      token: opts.token
    });
    out.push(...files);
    if (files.length < 100) break;
  }
  return out;
}

async function putDedupKeys(opts: {
  kv: KVNamespace;
  ttlSeconds: number;
  deliveryId: string;
  commentId: number;
}): Promise<void> {
  const ttl = { expirationTtl: opts.ttlSeconds };
  await Promise.all([
    opts.kv.put(`delivery:${opts.deliveryId}`, "1", ttl),
    opts.kv.put(`comment:${opts.commentId}`, "1", ttl)
  ]);
}

async function alreadyProcessed(opts: {
  kv: KVNamespace;
  deliveryId: string;
  commentId: number;
}): Promise<boolean> {
  const [a, b] = await Promise.all([
    opts.kv.get(`delivery:${opts.deliveryId}`),
    opts.kv.get(`comment:${opts.commentId}`)
  ]);
  return a !== null || b !== null;
}

function buildArticleText(filePath: string, content: string, maxChars: number): string {
  const prefix = `<!-- file_path: ${filePath} -->\n\n`;
  const body = content.length > maxChars ? `${content.slice(0, maxChars)}\n\n<!-- truncated -->\n` : content;
  return prefix + body;
}

async function runClaudeBravePipeline(opts: {
  anthropicApiKey: string;
  anthropicModel: string;
  temperature: number;
  braveApiKey: string;
  maxStatements: number;
  maxSearchResults: number;
  articleText: string;
}): Promise<{ markdown: string; debug: { statements: string[] } }> {
  const extracted = await anthropicCreateMessage({
    apiKey: opts.anthropicApiKey,
    model: opts.anthropicModel,
    system: EXTRACTING_PROMPT,
    messages: [{ role: "user", content: `<text>${opts.articleText}</text>` }],
    maxTokens: 1200,
    temperature: 0
  });

  const statements = extractAllBetweenTags("statement", extracted).slice(0, opts.maxStatements);

  const searches: Array<{ statement: string; formattedResults: string }> = [];
  for (const statement of statements) {
    const query = statement.length > 220 ? statement.slice(0, 220) : statement;
    const results = await braveSearchWeb({
      apiKey: opts.braveApiKey,
      query,
      count: opts.maxSearchResults
    });
    searches.push({ statement, formattedResults: formatBraveResults(results) });
  }

  const verifyInput = searches
    .map((s) => `<statement>${s.statement}</statement>\n${s.formattedResults}`)
    .join("\n\n");

  const verdicts = await anthropicCreateMessage({
    apiKey: opts.anthropicApiKey,
    model: opts.anthropicModel,
    system: VERDICT_PROMPT,
    messages: [{ role: "user", content: verifyInput }],
    maxTokens: 2200,
    temperature: 0
  });

  const answerRaw = await anthropicCreateMessage({
    apiKey: opts.anthropicApiKey,
    model: opts.anthropicModel,
    system: ANSWER_PROMPT,
    messages: [
      {
        role: "user",
        content: `<fact_checking_results>${verdicts}</fact_checking_results> <text>${opts.articleText}</text>`
      }
    ],
    maxTokens: 4000,
    temperature: opts.temperature
  });

  const answer = extractLastBetweenTags("answer", answerRaw) ?? answerRaw;
  return { markdown: answer.trim(), debug: { statements } };
}

async function processJob(job: ArticleCheckJob, env: Env): Promise<void> {
  const ttlSeconds = clampInt(env.DEDUP_TTL_SECONDS, 60 * 60 * 24 * 7, 60, 60 * 60 * 24 * 30);
  const maxStatements = clampInt(env.MAX_STATEMENTS, 12, 1, 30);
  const maxSearchResults = clampInt(env.MAX_SEARCH_RESULTS, 3, 1, 10);
  const maxFiles = clampInt(env.MAX_FILES, 1, 1, 5);
  const maxArticleChars = clampInt(env.MAX_ARTICLE_CHARS, 60_000, 5_000, 200_000);

  const model = env.ANTHROPIC_MODEL?.trim() || "claude-3-opus-20240229";
  const temperature = env.ANTHROPIC_TEMPERATURE ? Number(env.ANTHROPIC_TEMPERATURE) : 0;

  if (!env.GITHUB_APP_ID) throw new Error("missing_env:GITHUB_APP_ID");
  if (!env.GITHUB_APP_PRIVATE_KEY) throw new Error("missing_env:GITHUB_APP_PRIVATE_KEY");
  if (!env.ANTHROPIC_API_KEY) throw new Error("missing_env:ANTHROPIC_API_KEY");
  if (!env.BRAVE_API_KEY) throw new Error("missing_env:BRAVE_API_KEY");

  if (await alreadyProcessed({ kv: env.ARTICLECHECK_DEDUP, deliveryId: job.delivery_id, commentId: job.comment_id })) {
    logger.info("job_dedup_kv_hit", { delivery_id: job.delivery_id, comment_id: job.comment_id });
    return;
  }

  const token = await getInstallationAccessToken({
    installationId: job.installation_id,
    app: { appId: env.GITHUB_APP_ID, privateKeyPem: env.GITHUB_APP_PRIVATE_KEY }
  });

  // Marker-based dedup for KV eviction / replays.
  const m = marker(job.delivery_id, job.comment_id);
  const existingComments = await listIssueComments({
    repoFullName: job.repo_full_name,
    issueNumber: job.pr_number,
    token,
    perPage: 100
  });
  if (existingComments.some((c) => c.body.includes(m))) {
    logger.info("job_dedup_marker_hit", { delivery_id: job.delivery_id, comment_id: job.comment_id });
    await putDedupKeys({
      kv: env.ARTICLECHECK_DEDUP,
      ttlSeconds,
      deliveryId: job.delivery_id,
      commentId: job.comment_id
    });
    return;
  }

  const pull = await githubRequestJson<PullResponse>({
    url: `https://api.github.com/repos/${job.repo_full_name}/pulls/${job.pr_number}`,
    token
  });

  const files = await listPullFiles({ repoFullName: job.repo_full_name, prNumber: job.pr_number, token });
  const attackFiles = files
    .map((f) => f.filename)
    .filter((p) => p.startsWith("content/attacks/") && p.endsWith(".md"));

  if (attackFiles.length === 0) {
    const body = `${m}\n\nNo files under \`content/attacks/*.md\` were changed in this PR, so I did not run the article checker.\n`;
    await githubRequestJson({
      method: "POST",
      url: `https://api.github.com/repos/${job.repo_full_name}/issues/${job.pr_number}/comments`,
      token,
      body: { body }
    });
    await putDedupKeys({ kv: env.ARTICLECHECK_DEDUP, ttlSeconds, deliveryId: job.delivery_id, commentId: job.comment_id });
    return;
  }

  const selected = attackFiles.slice(0, maxFiles);
  const extraCount = attackFiles.length - selected.length;

  let commentBody = `${m}\n\n`;
  if (extraCount > 0) commentBody += `Note: only checked the first ${selected.length} file(s); ${extraCount} additional matching file(s) were skipped for resource bounds.\n\n`;

  for (const filePath of selected) {
    const raw = await githubRequestText({
      url: `https://api.github.com/repos/${job.repo_full_name}/contents/${filePath}?ref=${pull.head.sha}`,
      token,
      accept: "application/vnd.github.raw"
    });
    const articleText = buildArticleText(filePath, raw, maxArticleChars);

    logger.info("running_pipeline", {
      delivery_id: job.delivery_id,
      repo: job.repo_full_name,
      pr_number: job.pr_number,
      file: filePath
    });

    const result = await runClaudeBravePipeline({
      anthropicApiKey: env.ANTHROPIC_API_KEY,
      anthropicModel: model,
      temperature,
      braveApiKey: env.BRAVE_API_KEY,
      maxStatements,
      maxSearchResults,
      articleText
    });

    commentBody += `### ${filePath}\n\n${result.markdown}\n\n`;
  }

  // Post as a single comment to keep idempotency simple.
  await githubRequestJson({
    method: "POST",
    url: `https://api.github.com/repos/${job.repo_full_name}/issues/${job.pr_number}/comments`,
    token,
    body: { body: commentBody }
  });

  await putDedupKeys({ kv: env.ARTICLECHECK_DEDUP, ttlSeconds, deliveryId: job.delivery_id, commentId: job.comment_id });
  logger.info("job_completed", { delivery_id: job.delivery_id, repo: job.repo_full_name, pr_number: job.pr_number });
}

export default {
  async queue(batch: MessageBatch<ArticleCheckJob>, env: Env, ctx: ExecutionContext): Promise<void> {
    for (const message of batch.messages) {
      ctx.waitUntil(
        (async () => {
          try {
            await processJob(message.body, env);
            message.ack();
          } catch (err) {
            logger.error("job_failed", {
              delivery_id: message.body?.delivery_id,
              repo: message.body?.repo_full_name,
              pr_number: message.body?.pr_number,
              err: String(err)
            });
            message.retry();
          }
        })()
      );
    }
  }
};

