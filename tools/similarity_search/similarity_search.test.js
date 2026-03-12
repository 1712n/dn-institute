import { describe, it, expect, vi } from 'vitest';
import { handleRequest } from './similarity_search.js';

vi.mock('cloudflare-vectorize', () => ({
  getVectorDatabase: vi.fn(() => ({
    query: vi.fn(() => Promise.resolve([{ similarity: 0.9, id: '123' }])),
  })),
}));

describe('Similarity Search API', () => {
  it('should return a similarity score for a valid message', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Hello, world!' }),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result).toHaveProperty('similarity', 0.9);
  });

  it('should return a 400 error for a missing message', async () => {
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

  it('should return a 400 error for an invalid JSON body', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: 'invalid json',
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(400);
    expect(result).toHaveProperty('error', 'Invalid JSON body');
  });
});