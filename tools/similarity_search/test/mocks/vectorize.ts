// 🌰 Mock Vectorize database for testing
export const mockVectorizeIndex = {
  query: async (vector: number[], options?: { topK?: number }) => {
    // 🌰 Return mock similarity results
    const mockResults = [
      {
        id: "doc1",
        score: 0.95,
        metadata: { category: "blockchain", source: "test" }
      },
      {
        id: "doc2", 
        score: 0.87,
        metadata: { category: "crypto", source: "test" }
      },
      {
        id: "doc3",
        score: 0.72,
        metadata: { category: "defi", source: "test" }
      }
    ];

    const topK = options?.topK || 5;
    return mockResults.slice(0, topK);
  },

  insert: async (vectors: any[]) => {
    // 🌰 Mock insert operation
    return { ids: vectors.map((_, i) => `inserted_${i}`) };
  },

  upsert: async (vectors: any[]) => {
    // 🌰 Mock upsert operation
    return { ids: vectors.map((_, i) => `upserted_${i}`) };
  },

  deleteByIds: async (ids: string[]) => {
    // 🌰 Mock delete operation
    return { deleted: ids.length };
  },

  describe: async () => {
    return { dimensions: 768, count: 1000 };
  }
};