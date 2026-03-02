import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeEach(async () => {
    // 🌰 Start the worker in isolated environment
    worker = await unstable_dev('src/index.ts', {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: 'test-index',
        AI: 'mock-ai',
      },
    });
  });

  afterEach(async () => {
    // 🌰 Clean up worker
    await worker.stop();
  });

  describe('🌰 POST /search endpoint', () => {
    it('🌰 should return similarity scores for valid text input', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Bitcoin price reaches new all-time high amid institutional adoption',
          threshold: 0.7,
          limit: 5,
        }),
      });

      expect(response.status).toBe(200);
      const data = await response.json();

      expect(data).toHaveProperty('results');
      expect(Array.isArray(data.results)).toBe(true);
      expect(data.results.length).toBeLessThanOrEqual(5);

      if (data.results.length > 0) {
        expect(data.results[0]).toHaveProperty('score');
        expect(typeof data.results[0].score).toBe('number');
        expect(data.results[0].score).toBeGreaterThanOrEqual(0);
        expect(data.results[0].score).toBeLessThanOrEqual(1);
      }
    });

    it('🌰 should handle empty text input gracefully', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: '' }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('text is required');
    });

    it('🌰 should validate threshold parameter range', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Test query',
          threshold: 1.5, // Invalid: > 1
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain('threshold must be between 0 and 1');
    });

    it('🌰 should validate limit parameter range', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Test query',
          limit: 0, // Invalid: < 1
        }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain('limit must be between 1 and 20');
    });

    it('🌰 should handle missing Content-Type header', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        body: JSON.stringify({ text: 'Test query' }),
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain('Content-Type must be application/json');
    });

    it('🌰 should handle malformed JSON', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{ invalid json }',
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain('Invalid JSON');
    });
  });

  describe('🌰 GET /health endpoint', () => {
    it('🌰 should return health status', async () => {
      const response = await worker.fetch('/health');

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('status', 'healthy');
      expect(data).toHaveProperty('timestamp');
      expect(new Date(data.timestamp)).toBeInstanceOf(Date);
    });
  });

  describe('🌰 CORS headers', () => {
    it('🌰 should include CORS headers in responses', async () => {
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: 'Test query' }),
      });

      expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
      expect(response.headers.get('Access-Control-Allow-Methods')).toContain('POST');
      expect(response.headers.get('Access-Control-Allow-Headers')).toContain('Content-Type');
    });

    it('🌰 should handle preflight OPTIONS requests', async () => {
      const response = await worker.fetch('/search', {
        method: 'OPTIONS',
        headers: {
          'Origin': 'https://example.com',
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type',
        },
      });

      expect(response.status).toBe(200);
      expect(response.headers.get('Access-Control-Allow-Origin')).toBe('*');
    });
  });
