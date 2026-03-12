import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    // 🌰 Start the Cloudflare worker in dev mode for testing
    worker = await unstable_dev('src/index.ts', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: 'test-index',
        AI_MODEL: '@cf/baai/bge-base-en-v1.5',
        THRESHOLD: '0.85'
      }
    });
  });

  afterAll(async () => {
    // 🌰 Clean up the worker after tests
    await worker.stop();
  });

  describe('🌰 POST /search endpoint', () => {
    it('should return similarity scores for valid text input', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'This is a test message about cryptocurrency trading',
          limit: 5
        })
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      expect(data).toHaveProperty('results');
      expect(Array.isArray(data.results)).toBe(true);
      expect(data.results.length).toBeLessThanOrEqual(5);
      
      if (data.results.length > 0) {
        expect(data.results[0]).toHaveProperty('id');
        expect(data.results[0]).toHaveProperty('score');
        expect(typeof data.results[0].score).toBe('number');
        expect(data.results[0].score).toBeGreaterThanOrEqual(0);
        expect(data.results[0].score).toBeLessThanOrEqual(1);
      }
    });

    it('should handle empty text input gracefully', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: '' })
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('text is required');
    });

    it('should handle missing text field', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 10 })
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('text is required');
    });

    it('should respect limit parameter', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Testing limit parameter functionality',
          limit: 3
        })
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.results.length).toBeLessThanOrEqual(3);
    });

    it('should handle invalid limit parameter', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Testing invalid limit',
          limit: 'invalid'
        })
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });
  });

  describe('🌰 GET /health endpoint', () => {
    it('should return healthy status', async () => {
      const response = await worker.fetch('/health');
      
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('status');
      expect(data.status).toBe('healthy');
    });
  });

  describe('🌰 Error handling', () => {
    it('should handle non-existent endpoints', async () => {
      const response = await worker.fetch('/nonexistent');
      
      expect(response.status).toBe(404);
    });

    it('should handle invalid JSON in request body', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid json'
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should handle missing Content-Type header', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        body: JSON.stringify({ text: 'test' })
      });

      expect(response.status).toBe(400);
    });
  });

  describe('🌰 Performance tests', () => {
    it('should respond within acceptable time limits', async () => {
      const start = Date.now();
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Performance test message for response time validation',
          limit: 5
        })
      });
      const duration = Date.now() - start;

      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(5000); // 🌰 5 second timeout
    });
  });
});