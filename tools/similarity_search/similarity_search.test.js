import { describe, it, expect, vi } from 'vitest';
import { handleRequest } from './similarity_search.js';

vi.mock('cloudflare:vectorize', () => ({
  Vectorize: {
    get: vi.fn(() => ({
      query: vi.fn(() => [
        { id: '1', similarity: 0.9 },
        { id: '2', similarity: 0.8 },
      ]),
    })),
  },
}));

describe('Similarity Search API', () => {
  it('should return similarity scores for a given message', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'test message' }),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result).toEqual([
      { id: '1', similarity: 0.9 },
      { id: '2', similarity: 0.8 },
    ]);
  });

  it('should return 400 for invalid JSON', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: 'invalid json',
    });

    const response = await handleRequest(request);

    expect(response.status).toBe(400);
  });

  it('should return 400 for missing message field', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });

    const response = await handleRequest(request);

    expect(response.status).toBe(400);
  });
});