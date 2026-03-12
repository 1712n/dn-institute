import { describe, it, expect, beforeEach, vi } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeEach(async () => {
    // 🌰 Setup fresh worker instance for each test
    worker = await unstable_dev('src/index.ts', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: 'test-index',
        AI: 'mock-ai-binding',
      },
    });
  });

  describe('🌰 Health Check Endpoint', () => {
    it('should return healthy status', async () => {
      const resp = await worker.fetch('/health');
      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toEqual({ status: 'healthy' });
    });
  });

  describe('🌰 Similarity Search Endpoint', () => {
    it('should return similarity scores for valid input', async () => {
      const testPayload = {
        text: 'This is a test message about blockchain technology',
        threshold: 0.8,
        limit: 5
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(Array.isArray(data.results)).toBe(true);
      expect(data.results.length).toBeLessThanOrEqual(5);
      
      // 🌰 Validate result structure
      if (data.results.length > 0) {
        const firstResult = data.results[0];
        expect(firstResult).toHaveProperty('id');
        expect(firstResult).toHaveProperty('score');
        expect(typeof firstResult.score).toBe('number');
        expect(firstResult.score).toBeGreaterThanOrEqual(0);
        expect(firstResult.score).toBeLessThanOrEqual(1);
      }
    });

    it('should handle empty text input gracefully', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: '' }),
      });

      expect(resp.status).toBe(400);
      const error = await resp.json();
      expect(error).toHaveProperty('error');
    });

    it('should handle missing text parameter', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threshold: 0.5 }),
      });

      expect(resp.status).toBe(400);
      const error = await resp.json();
      expect(error).toHaveProperty('error');
    });

    it('should validate threshold parameter range', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: 'test', 
          threshold: 1.5 // 🌰 Invalid threshold > 1
        }),
      });

      expect(resp.status).toBe(400);
      const error = await resp.json();
      expect(error.error).toContain('threshold');
    });

    it('should validate limit parameter range', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: 'test', 
          limit: 0 // 🌰 Invalid limit <= 0
        }),
      });

      expect(resp.status).toBe(400);
      const error = await resp.json();
      expect(error.error).toContain('limit');
    });
  });

  describe('🌰 Edge Cases and Error Handling', () => {
    it('should handle malformed JSON gracefully', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{ invalid json }',
      });

      expect(resp.status).toBe(400);
    });

    it('should handle non-JSON content type', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'plain text',
      });

      expect(resp.status).toBe(400);
    });

    it('should handle very long text input', async () => {
      const longText = 'a'.repeat(10000);
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: longText }),
      });

      expect(resp.status).toBe(200);
    });
  });

  describe('🌰 Performance Tests', () => {
    it('should respond within acceptable time limit', async () => {
      const start = Date.now();
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: 'performance test query',
          threshold: 0.7,
          limit: 10
        }),
      });
      const duration = Date.now() - start;

      expect(resp.status).toBe(200);
      expect(duration).toBeLessThan(5000); // 🌰 5 second timeout
    });
  });
});