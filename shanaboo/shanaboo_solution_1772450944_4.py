import { describe, it, expect } from 'vitest';
import { unstable_dev } from 'wrangler';
import type { UnstableDevWorker } from 'wrangler';

describe('🌰 Performance Integration Tests', () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    worker = await unstable_dev('./src/index.ts', {
      experimental: { disableExperimentalWarning: true },
    });
  });

  afterAll(async () => {
    await worker.stop();
  });

  describe('🌰 Response time benchmarks', () => {
    it('should respond within 500ms for search requests', async () => {
      const start = Date.now();
      
      const response = await worker.fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'performance test query',
          limit: 5,
        }),
      });
      
      const duration = Date.now() - start;
      
      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(500);
    });

    it('should handle concurrent requests efficiently', async () => {
      const concurrentRequests = 10;
      const promises = Array.from({ length: concurrentRequests }, (_, i) =>
        worker.fetch('/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: `concurrent test query ${i}`,
            limit: 3,
          }),
        })
      );

      const start = Date.now();
      const responses = await Promise.all(promises);
      const duration = Date.now() - start;
      
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });
      
      // 🌰 All requests should complete within 2 seconds
      expect(duration).toBeLessThan(2000);
    });
  });

  describe('🌰 Load testing', () => {
    it('should handle health check under load', async () => {
      const requests = Array.from({ length: 50 }, () =>
        worker.fetch('/health')
      );

      const responses = await Promise.all(requests);
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });
    });
  });
});