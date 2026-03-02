import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createExecutionContext } from 'cloudflare:test';

// 🌰 Mock Cloudflare Workers AI and Vectorize
const mockVectorizeIndex = {
  query: vi.fn(),
  insert: vi.fn(),
  upsert: vi.fn(),
  delete: vi.fn(),
};

const mockAI = {
  run: vi.fn(),
};

describe('🌰 Vectorize Integration Tests', () => {
  let env: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    env = {
      VECTORIZE_INDEX: mockVectorizeIndex,
      AI: mockAI,
    };
  });

  describe('🌰 Vector embedding and search flow', () => {
    it('should generate embeddings and perform similarity search', async () => {
      // 🌰 Mock AI embedding response
      mockAI.run.mockResolvedValue({
        data: [0.1, 0.2, 0.3, 0.4, 0.5],
      });

      // 🌰 Mock Vectorize query response
      mockVectorizeIndex.query.mockResolvedValue({
        matches: [
          {
            id: 'doc1',
            score: 0.95,
            metadata: { title: 'Bitcoin Analysis', category: 'crypto' },
          },
          {
            id: 'doc2',
            score: 0.87,
            metadata: { title: 'Market Trends', category: 'finance' },
          },
        ],
      });

      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'cryptocurrency market analysis',
          limit: 10,
          threshold: 0.8,
        }),
      });

      const ctx = createExecutionContext();
      
      // 🌰 Import the worker
      const worker = await import('../../src/index');
      const response = await worker.default.fetch(request, env, ctx);
      
      expect(response.status).toBe(200);
      const data = await response.json();
      
      expect(mockAI.run).toHaveBeenCalledWith(
        '@cf/baai/bge-base-en-v1.5',
        { text: 'cryptocurrency market analysis' }
      );
      
      expect(mockVectorizeIndex.query).toHaveBeenCalledWith(
        [0.1, 0.2, 0.3, 0.4, 0.5],
        { topK: 10, returnValues: false, returnMetadata: true }
      );
      
      expect(data.results).toHaveLength(2);
      expect(data.results[0].score).toBe(0.95);
      expect(data.results[0].metadata.title).toBe('Bitcoin Analysis');
    });

    it('should handle empty vector search results', async () => {
      mockAI.run.mockResolvedValue({
        data: [0.1, 0.2, 0.3],
      });
      
      mockVectorizeIndex.query.mockResolvedValue({
        matches: [],
      });

      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'unique query with no matches' }),
      });

      const ctx = createExecutionContext();
      const worker = await import('../../src/index');
      const response = await worker.default.fetch(request, env, ctx);
      
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.results).toHaveLength(0);
    });

    it('should filter results by threshold', async () => {
      mockAI.run.mockResolvedValue({
        data: [0.1, 0.2, 0.3],
      });
      
      mockVectorizeIndex.query.mockResolvedValue({
        matches: [
          { id: 'doc1', score: 0.95, metadata: {} },
          { id: 'doc2', score: 0.65, metadata: {} },
          { id: 'doc3', score: 0.45, metadata: {} },
        ],
      });

      const request = new Request('http://localhost/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'test',
          threshold: 0.7,
        }),
      });

      const ctx = createExecutionContext();
      const worker = await import('../../src/index');
      const response = await worker.default.fetch(request, env, ctx);
      
      const data = await response.json();
      expect(data.results).toHaveLength(2);
      expect(data.results.every((r: any) => r.score >= 0.7)).toBe(true);
    });
  });
});