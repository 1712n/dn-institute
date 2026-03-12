import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    // 🌰 Start the worker for integration testing
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
    // 🌰 Clean up the worker
    await worker.stop();
  });

  describe('🌰 Health Check Endpoint', () => {
    it('should return healthy status', async () => {
      const resp = await worker.fetch('/health');
      expect(resp.status).toBe(200);
      
      const json = await resp.json() as { status: string };
      expect(json.status).toBe('healthy');
    });
  });

  describe('🌰 Similarity Search Functionality', () => {
    it('should return similarity scores for valid text', async () => {
      const testText = 'This is a test message about cryptocurrency trading';
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: testText })
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json() as {
        similarity: number;
        matches: Array<{
          id: string;
          score: number;
          metadata?: Record<string, any>;
        }>;
      };
      
      expect(json).toHaveProperty('similarity');
      expect(json).toHaveProperty('matches');
      expect(typeof json.similarity).toBe('number');
      expect(Array.isArray(json.matches)).toBe(true);
    });

    it('should handle empty text gracefully', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: '' })
      });

      expect(resp.status).toBe(400);
      
      const json = await resp.json() as { error: string };
      expect(json.error).toContain('text is required');
    });

    it('should handle missing text field', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      expect(resp.status).toBe(400);
      
      const json = await resp.json() as { error: string };
      expect(json.error).toContain('text is required');
    });

    it('should handle very long text input', async () => {
      const longText = 'a'.repeat(10000);
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: longText })
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json() as {
        similarity: number;
        matches: any[];
      };
      
      expect(json.similarity).toBeDefined();
      expect(json.matches).toBeDefined();
    });

    it('should handle special characters and unicode', async () => {
      const specialText = '🌰 Cryptocurrency news: BTC & ETH prices! 中文测试 🚀';
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: specialText })
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json() as {
        similarity: number;
        matches: any[];
      };
      
      expect(json.similarity).toBeDefined();
      expect(json.matches).toBeDefined();
    });
  });

  describe('🌰 Rate Limiting and Security', () => {
    it('should handle concurrent requests', async () => {
      const promises = Array.from({ length: 10 }, (_, i) => 
        worker.fetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: `concurrent test ${i}` })
        })
      );

      const responses = await Promise.all(promises);
      
      // 🌰 All requests should complete successfully
      responses.forEach(resp => {
        expect(resp.status).toBeOneOf([200, 429]);
      });
    });

    it('should reject non-JSON content type', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'plain text'
      });

      expect(resp.status).toBe(400);
      
      const json = await resp.json() as { error: string };
      expect(json.error).toContain('Content-Type must be application/json');
    });

    it('should reject GET requests to search endpoint', async () => {
      const resp = await worker.fetch('/search', {
        method: 'GET'
      });

      expect(resp.status).toBe(405);
    });
  });

  describe('🌰 Response Format Validation', () => {
    it('should return consistent response structure', async () => {
      const testText = 'Testing response format validation';
      
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: testText })
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json();
      
      // 🌰 Validate response structure
      expect(json).toHaveProperty('similarity');
      expect(json).toHaveProperty('matches');
      expect(typeof json.similarity).toBe('number');
      expect(json.similarity).toBeGreaterThanOrEqual(0);
      expect(json.similarity).toBeLessThanOrEqual(1);
      expect(Array.isArray(json.matches)).toBe(true);
      
      // 🌰 Validate match structure if matches exist
      if (json.matches.length > 0) {
        const firstMatch = json.matches[0];
        expect(firstMatch).toHaveProperty('id');
        expect(firstMatch).toHaveProperty('score');
        expect(typeof firstMatch.score).toBe('number');
      }
    });
  });
});