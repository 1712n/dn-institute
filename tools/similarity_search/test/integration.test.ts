import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    // 🌰 Initialize the worker for testing
    worker = await unstable_dev('./src/index.ts', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: 'test-index',
        AI_MODEL: '@cf/baai/bge-base-en-v1.5',
      },
    });
  });

  afterAll(async () => {
    // 🌰 Clean up the worker
    await worker.stop();
  });

  describe('🌰 POST /search endpoint', () => {
    it('should return similarity scores for valid query', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'cryptocurrency market analysis',
          limit: 5,
          threshold: 0.7,
        }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      expect(data).toHaveProperty('results');
      expect(Array.isArray(data.results)).toBe(true);
      expect(data.results.length).toBeLessThanOrEqual(5);
      
      if (data.results.length > 0) {
        expect(data.results[0]).toHaveProperty('id');
        expect(data.results[0]).toHaveProperty('score');
        expect(data.results[0]).toHaveProperty('metadata');
        expect(typeof data.results[0].score).toBe('number');
        expect(data.results[0].score).toBeGreaterThanOrEqual(0);
        expect(data.results[0].score).toBeLessThanOrEqual(1);
      }
    });

    it('should handle missing query parameter', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 5 }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('query');
    });

    it('should handle invalid limit parameter', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'test query',
          limit: 'invalid',
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should handle threshold parameter correctly', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'blockchain technology',
          threshold: 0.9,
        }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      if (data.results.length > 0) {
        data.results.forEach((result: any) => {
          expect(result.score).toBeGreaterThanOrEqual(0.9);
        });
      }
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

  describe('🌰 Error handling', () => {
    it('should handle malformed JSON', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid json',
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should handle empty request body', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should handle non-existent endpoints', async () => {
      const response = await worker.fetch('/nonexistent');
      
      expect(response.status).toBe(404);
    });
  });

  describe('🌰 Performance tests', () => {
    it('should respond within acceptable time limit', async () => {
      const start = Date.now();
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'performance test query',
          limit: 10,
        }),
      });
      const duration = Date.now() - start;

      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(5000); // 🌰 5 second timeout
    });

    it('should handle concurrent requests', async () => {
      const requests = Array(5).fill(null).map(() => 
        worker.fetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: 'concurrent test',
            limit: 3,
          }),
        })
      );

      const responses = await Promise.all(requests);
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });
    });
  });
});