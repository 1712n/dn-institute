import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeEach(async () => {
    // 🌰 Start the worker for each test
    worker = await unstable_dev('src/index.ts', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: 'test-index',
        AI: 'mock-ai',
      },
    });
  });

  afterEach(async () => {
    // 🌰 Clean up worker after each test
    if (worker) {
      await worker.stop();
    }
  });

  describe('🌰 POST /search endpoint', () => {
    it('🌰 should return similarity scores for valid request', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'test message for similarity search',
          threshold: 0.8,
          limit: 5,
        }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('results');
      expect(Array.isArray(data.results)).toBe(true);
      expect(data.results.length).toBeLessThanOrEqual(5);
    });

    it('🌰 should handle missing query parameter', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

    it('🌰 should handle invalid threshold values', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'test message',
          threshold: 1.5, // Invalid: should be 0-1
          limit: 5,
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('🌰 should handle negative limit values', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
 'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'test message',
          threshold: 0.8,
          limit: -1,
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('🌰 should handle empty query string', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: '',
          threshold: 0.8,
          limit: 5,
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });
  });

  describe('🌰 GET /health endpoint', () => {
    it('🌰 should return health status', async () => {
      const response = await worker.fetch('/health');
      
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data.status).toBe('healthy');
    });
  });

  describe('🌰 Error handling', () => {
    it('🌰 should handle non-existent endpoints', async () => {
      const response = await worker.fetch('/nonexistent');
      
      expect(response.status).toBe(404);
    });

    it('🌰 should handle invalid JSON in request body', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: 'invalid json',
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('🌰 should handle missing Content-Type header', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        body: JSON.stringify({
          query: 'test message',
          threshold: 0.8,
          limit: 5,
        }),
      });

      expect(response.status).toBe(400);
    });
  });

  describe('🌰 Performance tests', () => {
    it('🌰 should respond within acceptable time limit', async () => {
      const start = Date.now();
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'performance test query',
          threshold: 0.7,
          limit: 10,
        }),
      });
      const duration = Date.now() - start;

      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(5000); // 5 second timeout
    });
  });
});