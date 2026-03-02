import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { unstable_dev } from 'wrangler';
import { Vectorize } from '@cloudflare/workers-types';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker;
  let mockVectorize;

  // 🌰 Test vectors for consistent testing
  const testVectors = {
    cryptoNews: {
      id: 'test-crypto-1',
      values: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
      metadata: { category: 'crypto', source: 'news' }
    },
    blockchainTech: {
      id: 'test-blockchain-1',
      values: [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.05],
      metadata: { category: 'blockchain', source: 'tech' }
    },
    unrelatedTopic: {
      id: 'test-unrelated-1',
      values: [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05],
      metadata: { category: 'sports', source: 'news' }
    }
  };

  beforeAll(async () => {
    // 🌰 Mock Vectorize database
    mockVectorize = {
      query: vi.fn(),
      insert: vi.fn(),
      deleteByIds: vi.fn()
    };

    // 🌰 Start worker with mocked bindings
    worker = await unstable_dev('src/index.js', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: mockVectorize,
        AI: {
          run: vi.fn().mockResolvedValue({
            data: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
          })
        }
      }
    });
  });

  afterAll(async () => {
    await worker.stop();
  });

  describe('🌰 POST /search endpoint', () => {
    it('should return similarity scores for matching content', async () => {
      // 🌰 Mock successful vector search
      mockVectorize.query.mockResolvedValue({
        matches: [
          {
            id: testVectors.cryptoNews.id,
            score: 0.95,
            metadata: testVectors.cryptoNews.metadata
          },
          {
            id: testVectors.blockchainTech.id,
            score: 0.87,
            metadata: testVectors.blockchainTech.metadata
          }
        ]
      });

      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'Bitcoin reaches new all-time high amid institutional adoption'
        })
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      expect(data).toHaveProperty('results');
      expect(data.results).toHaveLength(2);
      expect(data.results[0]).toMatchObject({
        id: testVectors.cryptoNews.id,
        score: 0.95,
        metadata: testVectors.cryptoNews.metadata
      });
    });

    it('should handle empty search results gracefully', async () => {
      mockVectorize.query.mockResolvedValue({ matches: [] });

      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'Completely unrelated topic about space exploration'
        })
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.results).toEqual([]);
    });

    it('should validate required message field', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain('message is required');
    });

    it('should handle malformed JSON', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid json'
      });

      expect(response.status).toBe(400);
    });
  });

  describe('🌰 GET /health endpoint', () => {
    it('should return healthy status', async () => {
      const response = await worker.fetch('/health');
      
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toEqual({ status: 'healthy' });
    });
  });

  describe('🌰 Error handling', () => {
    it('should handle Vectorize connection failures', async () => {
      mockVectorize.query.mockRejectedValue(new Error('Vectorize connection failed'));

      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'Test message'
        })
      });

      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data.error).toContain('Search failed');
    });

    it('should handle AI service failures', async () => {
      // 🌰 Override AI mock to throw error
      worker.unstable_dev.vars.AI.run.mockRejectedValue(new Error('AI service unavailable'));

      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'Test message'
        })
      });

      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data.error).toContain('Failed to generate embedding');
    });
  });

  describe('🌰 Performance tests', () => {
    it('should respond within acceptable time limits', async () => {
      mockVectorize.query.mockResolvedValue({
        matches: [
          { id: 'perf-test-1', score: 0.9, metadata: { category: 'test' } }
        ]
      });

      const start = Date.now();
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: 'Performance test message'
        })
      });
      const duration = Date.now() - start;

      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(5000); // 🌰 5 second timeout
    });
  });
});