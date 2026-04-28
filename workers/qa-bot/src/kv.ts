/**
 * 🌰 KV-based idempotency store
 * Prevents duplicate processing of the same webhook event
 */

import { KVEntry } from './types';

const KV_PREFIX = 'qa:';

/**
 * Check if a comment has already been processed
 */
export async function isProcessed(
  kv: KVNamespace,
  commentId: number
): Promise<boolean> {
  const key = `${KV_PREFIX}${commentId}`;
  const entry = await kv.get(key);
  return entry !== null;
}

/**
 * Mark a comment as being processed (pending state)
 */
export async function markPending(
  kv: KVNamespace,
  commentId: number
): Promise<void> {
  const key = `${KV_PREFIX}${commentId}`;
  const entry: KVEntry = {
    commentId,
    processedAt: new Date().toISOString(),
    status: 'pending',
  };
  // TTL of 24 hours — stale pending entries auto-expire
  await kv.put(key, JSON.stringify(entry), { expirationTtl: 86400 });
}

/**
 * Mark a comment as completed
 */
export async function markCompleted(
  kv: KVNamespace,
  commentId: number,
  result?: string
): Promise<void> {
  const key = `${KV_PREFIX}${commentId}`;
  const entry: KVEntry = {
    commentId,
    processedAt: new Date().toISOString(),
    status: 'completed',
    result,
  };
  await kv.put(key, JSON.stringify(entry), { expirationTtl: 86400 });
}

/**
 * Mark a comment as failed (allows retry after TTL)
 */
export async function markFailed(
  kv: KVNamespace,
  commentId: number,
  error: string
): Promise<void> {
  const key = `${KV_PREFIX}${commentId}`;
  const entry: KVEntry = {
    commentId,
    processedAt: new Date().toISOString(),
    status: 'failed',
    result: error,
  };
  // Failed entries expire in 1 hour to allow retry
  await kv.put(key, JSON.stringify(entry), { expirationTtl: 3600 });
}

/**
 * Get the current status of a comment
 */
export async function getStatus(
  kv: KVNamespace,
  commentId: number
): Promise<KVEntry | null> {
  const key = `${KV_PREFIX}${commentId}`;
  const raw = await kv.get(key);
  if (!raw) return null;
  return JSON.parse(raw) as KVEntry;
}
