import { env, createExecutionContext, waitOnExecutionContext, SELF } from 'cloudflare:test';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import worker from '../src/index';

// 🌰 Test vectors for consistent testing
const testVectors = {
  cryptoNews: {
    text: "Bitcoin reaches new all-time high as institutional adoption accelerates",
    embedding: new Array(768).fill(0).map((_, i) => Math.sin(i * 0.1) * 0.5)
  },
  cryptoSecurity: {
    text: "Major exchange suffers security breach affecting millions in user funds",
    embedding: new Array(768).fill(0).map((_, i) => Math.cos(i * 0.1) * 0.5)
  },
  defiProtocol: {
    text: "New DeFi protocol launches innovative yield farming mechanism",
    embedding: new Array(768).fill(0).map((_, i) => Math.sin(i * 0.2) * 0.3)
  }
};

describe('🌰 Similarity Search API Integration Tests', () => {
  let vectorizeIndex: any;

  beforeEach(async () => {
    // 🌰 Setup test environment with mock Vectorize index
    vectorizeIndex = {
      insert: vi.fn(),
      query: vi.fn(),
      deleteByIds: vi.fn(),
      describe: vi.fn()
    };
    
    // Mock the Vectorize binding
    env.VECTORIZE_INDEX = vectorizeIndex;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('🌰 Health Check Endpoint', () => {
    it('should return healthy status', async () => {
      const request = new Request('http://localhost/health');
      const ctx = createExecutionContext();
      
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);
      
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toEqual({ status: 'healthy', service: 'similarity-search' });
    });
  });

  describe('🌰 Similarity Search Functionality', () => {
    it('should return similarity scores for matching vectors', async () => {
      const mockQueryResult = {
        matches: [
          { id: '1', score: 0.95, vector: testVectors.cryptoNews.embedding },
          { id: '2', score: 0.78, vector: testVectors.cryptoSecurity.embedding }
        ]
      };
      
      vectorizeIndex.query.mockResolvedValue(mockQueryResult);

      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: testVectors.cryptoNews.text,
          threshold: 0.8
        })
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('matches');
      expect(data.matches).toHaveLength(2);
      expect(data.matches[0].score).toBeGreaterThanOrEqual(0.8);
    });

    it('should handle empty search results gracefully', async () => {
      vectorizeIndex.query.mockResolvedValue({ matches: [] });

      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'Completely unrelated text',
          threshold: 0.9
        })
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.matches).toHaveLength(0);
    });

    it('should validate required fields', async () => {
      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(data.error).toContain('text');
    });
  });

  describe('🌰 Vector Insertion Tests', () => {
    it('should insert vectors successfully', async () => {
      vectorizeIndex.insert.mockResolvedValue({ ids: ['1', '2', '3'] });

      const request = new Request('http://localhost/vectors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vectors: [
            { id: '1', values: testVectors.cryptoNews.embedding, metadata: { text: testVectors.cryptoNews.text } },
            { id: '2', values: testVectors.cryptoSecurity.embedding, metadata: { text: testVectors.cryptoSecurity.text } }
          ]
        })
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(201);
      const data = await response.json();
      expect(data).toHaveProperty('inserted');
      expect(data.inserted).toBe(3);
    });

    it('should handle vector insertion errors', async () => {
      vectorizeIndex.insert.mockRejectedValue(new Error('Vector dimension mismatch'));

      const request = new Request('http://localhost/vectors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vectors: [{ id: '1', values: [1, 2, 3], metadata: { text: 'test' } }]
        })
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(500);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });
  });

  describe('🌰 Rate Limiting and Security', () => {
    it('should handle malformed JSON gracefully', async () => {
      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid json'
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
    });

    it('should reject non-JSON content type', async () => {
      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'plain text'
      });

      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data.error).toContain('Content-Type');
    });
  });

  describe('🌰 Performance Tests', () => {
    it('should respond within acceptable time limits', async () => {
      vectorizeIndex.query.mockImplementation(async () => ({
        matches: Array(10).fill(null).map((_, i) => ({
          id: `id-${i}`,
          score: 0.8 + Math.random() * 0.2,
          vector: new Array(768).fill(0)
        }))
      }));

      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: 'performance test query',
          threshold: 0.8
        })
      });

      const start = Date.now();
      const ctx = createExecutionContext();
      const response = await worker.fetch(request, env, ctx);
      await waitOnExecutionContext(ctx);
      const duration = Date.now() - start;

      expect(response.status).toBe(200);
      expect(duration).toBeLessThan(1000); // 🌰 Should respond within 1 second
    });
  });
});