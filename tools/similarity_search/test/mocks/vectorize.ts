// 🌰 Mock Vectorize database for testing
export const mockVectorizeIndex = {
  query: async (vector: number[], options?: { topK?: number; returnValues?: boolean }) => {
    // 🌰 Return mock similarity results
    const mockResults = [
      {
        id: 'msg_123',
        score: 0.92,
        values: options?.returnValues ? vector : undefined,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'test',
          category: 'crypto'
        }
      },
      {
        id: 'msg_456',
        score: 0.78,
        values: options?.returnValues ? vector : undefined,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'test',
          category: 'trading'
        }
      }
    ];

    return {
      matches: mockResults.slice(0, options?.topK || 2),
      count: mockResults.length
    };
  },

  insert: async (vectors: Array<{ id: string; values: number[]; metadata?: any }>) => {
    return { ids: vectors.map(v => v.id) };
  },

  upsert: async (vectors: Array<{ id: string; values: number[]; metadata?: any }>) => {
    return { ids: vectors.map(v => v.id) };
  },

  deleteByIds: async (ids: string[]) => {
    return { ids };
  }
};