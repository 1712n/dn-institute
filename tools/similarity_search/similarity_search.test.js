import { describe, it, expect, vi } from 'vitest';
import { handleRequest } from './similarity_search.js';

describe('Similarity Search API', () => {
  it('should return a similarity score for a valid input', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'test message' }),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result).toHaveProperty('similarity_score');
    expect(typeof result.similarity_score).toBe('number');
  });

  it('should return a 400 error for invalid JSON', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: 'invalid json',
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(400);
    expect(result).toHaveProperty('error', 'Invalid JSON');
  });

  it('should return a 400 error for missing message field', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(400);
    expect(result).toHaveProperty('error', 'Message field is required');
  });

  it('should handle database errors gracefully', async () => {
    vi.mock('./vectorize.js', () => ({
      search: () => { throw new Error('Database error'); }
    }));

    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'test message' }),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(500);
    expect(result).toHaveProperty('error', 'Internal Server Error');
  });
});