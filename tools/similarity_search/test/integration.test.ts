import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeEach(async () => {
    // 🌰 Start the worker in dev mode for testing
    worker = await unstable_dev('src/index.ts', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: 'test-index',
        AI: 'mock-ai',
      },
    });
  });

  afterEach(async () => {
    // 🌰 Clean up the worker
    await worker.stop();
  });

  describe('🌰 POST /search endpoint', () => {
    it('should return similarity scores for valid search request', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'Bitcoin price reaches new all-time high',
          threshold: 0.8,
          limit: 5,
        }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      expect(data).toHaveProperty('results');
      expect(Array.isArray(data.results)).toBe(true);
      expect(data).toHaveProperty('query');
      expect(data.query).toBe('Bitcoin price reaches new all-time high');
    });

    it('should handle missing query parameter', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          threshold: 0.8,
          limit: 5,
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('query');
    });

    it('should handle invalid threshold values', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'test query',
          threshold: 1.5,
          limit: 5,
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should handle negative limit values', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'test query',
          threshold: 0.8,
          limit: -1,
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });
  });

  describe('🌰 GET /health endpoint', () => {
    it('should return health status', async () => {
      const response = await worker.fetch('/health');
      
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data.status).toBe('healthy');
    });
  });

  describe('🌰 Rate limiting and security', () => {
    it('should handle concurrent requests gracefully', async () => {
      const requests = Array(10).fill(null).map(() => 
        worker.fetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: 'concurrent test',
            threshold: 0.8,
            limit: 5,
          }),
        })
      );

      const responses = await Promise.all(requests);
      responses.forEach(response => {
        expect(response.status).toBeOneOf([200, 429]);
      });
    });

    it('should reject requests with invalid content type', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'invalid body',
      });

      expect(response.status).toBe(400);
    });
  });

  describe('🌰 Response format validation', () => {
    it('should return properly formatted similarity results', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'Ethereum market analysis',
          threshold: 0.7,
          limit: 3,
        }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      expect(data.results).toBeDefined();
      if (data.results.length > 0) {
        const result = data.results[0];
        expect(result).toHaveProperty('id');
        expect(result).toHaveProperty('score');
        expect(result).toHaveProperty('text');
        expect(typeof result.score).toBe('number');
        expect(result.score).toBeGreaterThanOrEqual(0);
        expect(result.score).toBeLessThanOrEqual(1);
      }
    });
  });
});