/**
 * 🌰 Type definitions for QA Bot Worker
 */

export interface Env {
  // GitHub App
  APP_ID: string;
  APP_PRIVATE_KEY: string;
  WEBHOOK_SECRET: string;

  // LLM
  ANTHROPIC_API_KEY: string;
  BRAVE_API_KEY: string;

  // KV Namespace for idempotency
  QA_KV: KVNamespace;
}

export interface WebhookPayload {
  action: string;
  comment?: {
    id: number;
    body: string;
    user: { login: string };
  };
  issue?: {
    number: number;
    pull_request?: { url: string };
  };
  repository: {
    full_name: string;
    owner: { login: string };
  };
  installation?: {
    id: number;
  };
}

export interface PRDiff {
  filename: string;
  status: string;
  additions: number;
  deletions: number;
  changes: string;
  patch?: string;
}

export interface ArticleAnalysis {
  quality_score: number;
  factual_accuracy: number;
  source_diversity: number;
  issues: string[];
  suggestions: string[];
  sources: { title: string; url: string }[];
}

export interface KVEntry {
  commentId: number;
  processedAt: string;
  status: 'pending' | 'completed' | 'failed';
  result?: string;
}

export interface CheckResult {
  success: boolean;
  commentBody: string;
  error?: string;
}
