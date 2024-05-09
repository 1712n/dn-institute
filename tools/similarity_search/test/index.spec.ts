import { env, createExecutionContext, waitOnExecutionContext } from 'cloudflare:test';
import { describe, it, expect } from 'vitest';
import app from '../src/index';

describe('Authentication', () => {
  it('returns 401 Unauthorized when API key is missing or invalid', async () => {
    const request = new Request('https://example.com/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: 'Sample text',
        namespace: 'test-namespace',
      }),
    });

    const ctx = createExecutionContext();
    const response = await app.fetch(request, env, ctx);
    await waitOnExecutionContext(ctx);

    expect(response.status).toBe(401);
    expect(await response.text()).toBe('Unauthorized');
  });
});
