export interface Env {
  GITHUB_WEBHOOK_SECRET: string;
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;
  WIKI_REVIEWERS: string;
  DEDUP_KV: KVNamespace;
  PIPELINE_QUEUE: Queue;
  // Optional overrides
  ANTHROPIC_MODEL?: string;
  ANTHROPIC_MAX_TOKENS?: string;
}

export interface WebhookPayload {
  action: string;
  comment: {
    id: number;
    body: string;
    user: { login: string };
  };
  issue: {
    number: number;
    pull_request?: { url: string; diff_url: string; html_url: string };
  };
  repository: {
    full_name: string;
  };
}

export interface DiffFile {
  header: string;
  bodySegments: Array<{ header: string; body: string }>;
}

/** Message payload enqueued for the pipeline consumer. */
export interface PipelineJob {
  repo: string;
  prNumber: number;
  diffUrl: string;
}
