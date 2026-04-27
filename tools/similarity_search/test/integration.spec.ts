import { SELF, env } from 'cloudflare:test';
import { describe, expect, it, vi } from 'vitest';

const post = (body: unknown, key?: string) =>
  new Request('https://example.com/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(key ? { 'X-API-Key': key } : {}),
    },
    body: JSON.stringify(body),
  });

describe('Similarity Search worker - auth', () => {
  it('rejects requests with no X-API-Key (401)', async () => {
    const res = await SELF.fetch(post({ text: 'hello', namespace: 'docs' }));
    expect(res.status).toBe(401);
  });

  it('rejects requests with wrong X-API-Key (401)', async () => {
    const res = await SELF.fetch(post({ text: 'hello', namespace: 'docs' }, 'bad'));
    expect(res.status).toBe(401);
  });

  it('accepts requests with correct X-API-Key', async () => {
    vi.spyOn(env.AI, 'run').mockResolvedValue({ data: [[0.1, 0.2, 0.3]] } as any);
    vi.spyOn(env.VECTORIZE, 'query').mockResolvedValue({
      matches: [{ id: 'doc-1', score: 0.92 }],
    } as any);
    const res = await SELF.fetch(post({ text: 'hello', namespace: 'docs' }, 'test-key'));
    expect(res.status).toBe(200);
    const body = await res.json() as { score: number };
    expect(body.score).toBe(0.92);
  });
});

describe('Similarity Search worker - input validation', () => {
  it('returns 400 when text is missing', async () => {
    const res = await SELF.fetch(post({ namespace: 'docs' }, 'test-key'));
    expect(res.status).toBe(400);
  });

  it('returns 400 when namespace is missing', async () => {
    const res = await SELF.fetch(post({ text: 'hello' }, 'test-key'));
    expect(res.status).toBe(400);
  });
});

describe('Similarity Search worker - namespace isolation', () => {
  it('queries the requested namespace with topK 1', async () => {
    const querySpy = vi.spyOn(env.VECTORIZE, 'query').mockResolvedValue({
      matches: [{ id: 'doc-7', score: 0.71 }],
    } as any);
    vi.spyOn(env.AI, 'run').mockResolvedValue({ data: [[0.5, 0.5, 0.5]] } as any);
    await SELF.fetch(post({ text: 'topic A', namespace: 'tickets' }, 'test-key'));
    expect(querySpy).toHaveBeenCalledWith(
      expect.any(Array),
      expect.objectContaining({ namespace: 'tickets', topK: 1 }),
    );
  });
});

describe('Similarity Search worker - failure modes', () => {
  it('handles AI binding throwing', async () => {
    vi.spyOn(env.AI, 'run').mockRejectedValue(new Error('AI down'));
    const res = await SELF.fetch(post({ text: 'foo', namespace: 'docs' }, 'test-key'));
    expect([500, 502]).toContain(res.status);
  });
});

describe('Similarity Search worker - concurrency', () => {
  it('handles 10 concurrent requests', async () => {
    vi.spyOn(env.AI, 'run').mockResolvedValue({ data: [[0.1, 0.2]] } as any);
    vi.spyOn(env.VECTORIZE, 'query').mockResolvedValue({
      matches: [{ id: 'doc-1', score: 0.5 }],
    } as any);
    const reqs = Array.from({ length: 10 }, () =>
      SELF.fetch(post({ text: 'hello', namespace: 'docs' }, 'test-key')),
    );
    const results = await Promise.all(reqs);
    for (const r of results) expect(r.status).toBe(200);
  });
});
