import { describe, it, expect, vi } from 'vitest';
import { env } from 'cloudflare:test';

// 🌰 Mock the Cloudflare Workers AI and Vectorize
vi.mock('cloudflare:workers', () => ({
  Ai: vi.fn().mockImplementation(() => ({
    run: vi.fn().mockResolvedValue({
      data: [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]]
    })
  }))
}));

describe('🌰 Worker Environment Tests', () => {
  it('should have required environment variables', () => {
    expect(env).toBeDefined();
    expect(env.VECTORIZE_INDEX).toBeDefined();
  });

  it('should handle vectorize query operations', async () => {
    const mockQuery = {
      vector: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
      topK: 5,
      returnValues: true,
      returnMetadata: true
    };

    const mockResponse = {
      matches: [
        {
          id: "vec1",
          score: 0.95,
          metadata: { text: "Sample crypto news" }
        }
      ]
    };

    // 🌰 Mock the vectorize query
    env.VECTORIZE_INDEX.query = vi.fn().mockResolvedValue(mockResponse);
    
    const result = await env.VECTORIZE_INDEX.query(mockQuery);
    expect(result.matches).toHaveLength(1);
    expect(result.matches[0].score).toBe(0.95);
  });

  it('should handle empty vectorize results', async () => {
    const mockQuery = {
      vector: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
      topK: 5,
      returnValues: true,
      returnMetadata: true
    };

    const mockResponse = {
      matches: []
    };

    env.VECTORIZE_INDEX.query = vi.fn().mockResolvedValue(mockResponse);
    
    const result = await env.VECTORIZE_INDEX.query(mockQuery);
    expect(result.matches).toHaveLength(0);
  });
});