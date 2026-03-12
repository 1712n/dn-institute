import { describe, it, expect, vi } from 'vitest';
import { handleRequest } from './similarity_search.js';

vi.mock('cloudflare-vectorize', () => ({
  getVectorDatabase: vi.fn(() => ({
    query: vi.fn(() => Promise.resolve([{ similarity: 0.9, id: '123' }])),
  })),
}));

describe('Similarity Search API', () => {
  it('should return a similarity score for a valid request', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'test message' }),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result).toHaveProperty('similarity', 0.9);
  });

  it('should return a 400 error for a request without a message', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(400);
    expect(result).toHaveProperty('error', 'Message is required');
  });

  it('should return a 500 error for an internal server error', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'test message' }),
    });

    vi.mocked(globalThis.getVectorDatabase).mockImplementationOnce(() => ({
      query: vi.fn(() => Promise.reject(new Error('Internal Server Error'))),
    }));

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(500);
    expect(result).toHaveProperty('error', 'Internal Server Error');
  });
});