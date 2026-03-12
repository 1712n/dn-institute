import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { unstable_dev } from 'wrangler';

describe('🌰 Similarity Search API Integration Tests', () => {
  let worker;

  beforeAll(async () => {
    // 🌰 Start the worker for integration testing
    worker = await unstable_dev('src/index.js', {
      experimental: { disableExperimentalWarning: true },
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
      
      const json = await resp.json();
      expect(json).toEqual({ status: 'healthy' });
    });
  });

  describe('🌰 Similarity Search Functionality', () => {
    it('should return similarity scores for valid text', async () => {
      const testPayload = {
        text: 'Bitcoin price reaches new all-time high amid institutional adoption',
        threshold: 0.7
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json();
      expect(json).toHaveProperty('similarities');
      expect(Array.isArray(json.similarities)).toBe(true);
      expect(json).toHaveProperty('query');
      expect(json.query).toBe(testPayload.text);
    });

    it('should handle empty text gracefully', async () => {
      const testPayload = {
        text: '',
        threshold: 0.5
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(400);
      
      const json = await resp.json();
      expect(json).toHaveProperty('error');
      expect(json.error).toContain('text');
    });

    it('should handle missing threshold parameter', async () => {
      const testPayload = {
        text: 'Ethereum 2.0 staking rewards increase'
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json();
      expect(json).toHaveProperty('similarities');
      expect(json).toHaveProperty('threshold');
      expect(json.threshold).toBe(0.8); // Default threshold
    });

    it('should handle invalid threshold values', async () => {
      const testPayload = {
        text: 'DeFi protocols see massive TVL growth',
        threshold: 1.5
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(400);
      
      const json = await resp.json();
      expect(json).toHaveProperty('error');
      expect(json.error).toContain('threshold');
    });

    it('should handle very long text inputs', async () => {
      const longText = 'a'.repeat(5000);
      const testPayload = {
        text: longText,
        threshold: 0.6
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json();
      expect(json).toHaveProperty('similarities');
      expect(json.query.length).toBe(5000);
    });

    it('should handle special characters and unicode', async () => {
      const testPayload = {
        text: '🌰 Bitcoin & Ethereum: 加密货币市场分析 2024 📈',
        threshold: 0.5
      };

      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });

      expect(resp.status).toBe(200);
      
      const json = await resp.json();
      expect(json).toHaveProperty('similarities');
      expect(json.query).toBe(testPayload.text);
    });
  });

  describe('🌰 Error Handling', () => {
    it('should return 405 for non-POST methods on /search', async () => {
      const resp = await worker.fetch('/search', {
        method: 'GET',
      });

      expect(resp.status).toBe(405);
    });

    it('should return 404 for non-existent endpoints', async () => {
      const resp = await worker.fetch('/nonexistent');

      expect(resp.status).toBe(404);
    });

    it('should handle malformed JSON gracefully', async () => {
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{ invalid json }',
      });

      expect(resp.status).toBe(400);
      
      const json = await resp.json();
      expect(json).toHaveProperty('error');
    });
  });

  describe('🌰 Performance Tests', () => {
    it('should respond within reasonable time', async () => {
      const testPayload = {
        text: 'Bitcoin market analysis and price prediction',
        threshold: 0.7
      };

      const start = Date.now();
      const resp = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testPayload),
      });
      const duration = Date.now() - start;

      expect(resp.status).toBe(200);
      expect(duration).toBeLessThan(5000); // 5 second timeout
    });
  });
});