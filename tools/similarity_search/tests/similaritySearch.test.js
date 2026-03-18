import { describe, it, expect } from 'vitest';
import { handleRequest } from '../index.js';

describe('Similarity Search API', () => {
  it('should return a similarity score for a given message', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: 'Hello, world!' }),
    });

    const response = await handleRequest(request);
    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result).toHaveProperty('similarityScore');
    expect(typeof result.similarityScore).toBe('number');
  });

  it('should handle invalid JSON gracefully', async () => {
    const request = new Request('http://localhost/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: 'invalid json',
    });

    const response = await handleRequest(request);
    expect(response.status).toBe(400);
  });
});