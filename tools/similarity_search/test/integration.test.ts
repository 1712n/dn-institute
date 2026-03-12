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
        AI_MODEL: '@cf/baai/bge-base-en-v1.5',
        THRESHOLD: '0.85',
      },
    });
  });

  afterEach(async () => {
    // 🌰 Clean up after each test
    await worker.stop();
  });

  describe('🌰 Health Check Endpoint', () => {
    it('should return healthy status', async () => {
      const resp = await worker.fetch('/health');
      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toEqual({
        status: 'healthy',
        service: 'similarity-search',
        version: expect.any(String),
      });
    });
  });

  describe('🌰 Similarity Search Endpoint', () => {
    it('should return similarity scores for valid text', async () => {
      const testText = 'This is a test message about blockchain technology';
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: testText }),
      });

      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toHaveProperty('similarity');
      expect(typeof data.similarity).toBe('number');
      expect(data.similarity).toBeGreaterThanOrEqual(0);
      expect(data.similarity).toBeLessThanOrEqual(1);
      expect(data).toHaveProperty('matches');
      expect(Array.isArray(data.matches)).toBe(true);
    });

    it('should handle empty text gracefully', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: '' }),
      });

      expect(resp.status).toBe(400);
      const data = await resp.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('text is required');
    });

    it('should handle missing text field', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });

      expect(resp.status).toBe(400);
      const data = await resp.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('text is required');
    });

    it('should handle non-JSON requests', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'plain text',
      });

      expect(resp.status).toBe(400);
      const data = await resp.json();
      expect(data).toHaveProperty('error');
    });

    it('should handle very long text inputs', async () => {
      const longText = 'a'.repeat(10000);
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: longText }),
      });

      expect(resp.status).toBe(200);
      const data = await resp.json();
      expect(data).toHaveProperty('similarity');
    });

    it('should handle special characters and unicode', async () => {
      const specialText = '🌰 Testing with emojis and unicode: 你好世界! @#$%^&*()';
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: specialText }),
      });

      expect(resp.status).toBe(200);
      const data = await resp.json();
      expect(data).toHaveProperty('similarity');
    });
  });

  describe('🌰 Batch Similarity Search', () => {
    it('should process multiple texts efficiently', async () => {
      const texts = [
        'Blockchain technology is revolutionary',
        'Cryptocurrency markets are volatile',
        'DeFi protocols enable decentralized finance',
      ];

      const promises = texts.map(text => 
        worker.fetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        })
      );

      const responses = await Promise.all(promises);
      
      responses.forEach(resp => {
        expect(resp.status).toBe(200);
      });

      const results = await Promise.all(
        responses.map(r => r.json())
      );

      results.forEach(result => {
        expect(result).toHaveProperty('similarity');
        expect(result).toHaveProperty('matches');
      });
    });
  });

  describe('🌰 Error Handling & Edge Cases', () => {
    it('should handle malformed JSON', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{ invalid json }',
      });

      expect(resp.status).toBe(400);
    });

    it('should handle null text values', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: null }),
      });

      expect(resp.status).toBe(400);
    });

    it('should handle array text values', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: ['array', 'of', 'text'] }),
      });

      expect(resp.status).toBe(400);
    });
  });
});