import { describe, it, expect, vi } from 'vitest';
import { handleRequest } from './similarity_search.js';

vi.mock('https://api.cloudflare.com/client/v4/accounts/{account_id}/vectorize/v1/namespaces/{namespace}/query', () => {
  return {
    default: vi.fn(() => ({
      json: vi.fn(() => Promise.resolve({
        matches: [
          { id: '1', score: 0.95 },
          { id: '2', score: 0.85 }
        ]
      }))
    }))
  };
});

describe('Similarity Search API', () => {
  it('should return a similarity score for a given message', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Test message' })
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result).toHaveProperty('matches');
    expect(result.matches).toHaveLength(2);
    expect(result.matches[0]).toHaveProperty('id', '1');
    expect(result.matches[0]).toHaveProperty('score', 0.95);
    expect(result.matches[1]).toHaveProperty('id', '2');
    expect(result.matches[1]).toHaveProperty('score', 0.85);
  });

  it('should handle invalid JSON input gracefully', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: 'invalid json'
    });

    const response = await handleRequest(request);

    expect(response.status).toBe(400);
    expect(await response.text()).toBe('Invalid JSON input');
  });

  it('should handle missing message field gracefully', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });

    const response = await handleRequest(request);

    expect(response.status).toBe(400);
    expect(await response.text()).toBe('Message field is required');
  });
});