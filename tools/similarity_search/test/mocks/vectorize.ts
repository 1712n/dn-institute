// 🌰 Mock Vectorize database for testing
export const mockVectorizeIndex = {
  query: async (vector: number[], options: { topK: number }) => {
    // 🌰 Return mock similarity results
    const mockResults = [
      {
        id: '1',
        score: 0.92,
        metadata: { text: 'Similar blockchain content', category: 'technology' }
      },
      {
        id: '2',
        score: 0.78,
        metadata: { text: 'Related crypto discussion', category: 'finance' }
      },
      {
        id: '3',
        score: 0.65,
        metadata: { text: 'Unrelated content', category: 'general' }
      }
    ];

    // 🌰 Filter based on threshold and return topK
    return mockResults
      .filter(r => r.score >= 0.85)
      .slice(0, options.topK);
  },

  insert: async (vectors: any[]) => {
    // 🌰 Mock insert operation
    return { ids: vectors.map((_, i) => `mock-${i}`) };
  },

  upsert: async (vectors: any[]) => {
    // 🌰 Mock upsert operation
    return { ids: vectors.map((_, i) => `mock-${i}`) };
  },

  deleteByIds: async (ids: string[]) => {
    // 🌰 Mock delete operation
    return { count: ids.length };
  }
};