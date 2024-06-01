import { describe, it, expect, vi } from 'vitest';
import worker from '../src/worker.js';

describe('Cloudflare Worker', () => {
  const env = {
    DURABLE_OBJECT_NAMESPACE: {
      idFromName: vi.fn().mockReturnValue({
        name: 'test-id',
      }),
      get: vi.fn().mockReturnValue({
        fetch: vi.fn().mockResolvedValue(new Response('Processing started')),
      }),
    },
  };

  it('should return 405 for non-POST requests', async () => {
    const request = new Request('http://localhost', { method: 'GET' });
    const response = await worker.fetch(request, env);

    expect(response.status).toBe(405);
    expect(await response.text()).toBe('Method not allowed');
  });

  it('should return 200 and process in the background for POST requests', async () => {
    const payload = {
      issue: {
        pull_request: {
          url: 'http://localhost/pull/1',
        },
      },
    };

    const request = new Request('http://localhost', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-GitHub-Delivery': 'test-event-id' },
      body: JSON.stringify(payload),
    });

    const response = await worker.fetch(request, env);

    expect(response.status).toBe(200);
    expect(await response.text()).toBe('Request received, processing in background');
    expect(env.DURABLE_OBJECT_NAMESPACE.idFromName).toHaveBeenCalledWith('http://localhost/pull/1');
    expect(env.DURABLE_OBJECT_NAMESPACE.get).toHaveBeenCalled();
    expect(env.DURABLE_OBJECT_NAMESPACE.get().fetch).toHaveBeenCalledWith(
      'http://dummy/process',
      expect.objectContaining({
        method: 'POST',
        headers: expect.any(Object),
        body: JSON.stringify({ payload }),
      })
    );
  });
});