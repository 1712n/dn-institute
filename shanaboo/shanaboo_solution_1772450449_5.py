// 🌰 Tests for the QA Bot Worker
import { unstable_dev } from 'wrangler';
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('🌰 QA Bot Worker', () => {
  let worker;

  beforeAll(async () => {
    worker = await unstable_dev('worker/index.js', {
      experimental: { disableExperimentalWarning: true },
    });
  });

  afterAll(async () => {
    await worker.stop();
  });

  it('should return 200 for health check', async () => {
    const resp = await worker.fetch('/');
    expect(resp.status).toBe(200);
    const text = await resp.text();
    expect(text).toContain('🌰');
  });

  it('should return 400 for missing headers', async () => {
    const resp = await worker.fetch('/webhook', {
      method: 'POST',
      body: JSON.stringify({}),
    });
    expect(resp.status).toBe(400);
  });

  it('should return 401 for invalid signature', async () => {
    const resp = await worker.fetch('/webhook', {
      method: 'POST',
      headers: {
        'x-github-event': 'pull_request',
        'x-hub-signature-256': 'invalid',
      },
      body: JSON.stringify({}),
    });
    expect(resp.status).toBe(401);
  });

  it('should return 200 for non-PR events', async () => {
    const payload = {
      action: 'opened',
      repository: { name: 'test', owner: { login: 'test' } },
      pull_request: { number: 1 },
    };
    
    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify(payload));
    const signature = await crypto.subtle.digest('SHA-256', data);
    const signatureHex = Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    const resp = await worker.fetch('/webhook', {
      method: 'POST',
      headers: {
        'x-github-event': 'push',
        'x-hub-signature-256': `sha256=${signatureHex}`,
      },
      body: JSON.stringify(payload),
    });
    expect(resp.status).toBe(200);
  });
});