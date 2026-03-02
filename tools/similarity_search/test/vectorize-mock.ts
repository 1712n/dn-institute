// 🌰 Mock Vectorize index for testing
export const mockVectorizeIndex = {
  async insert(vectors: any[]) {
    return { ids: vectors.map((_, i) => `vec_${i}`) };
  },

  async query(vector: number[], options: any = {}) {
    const mockResults = [
      {
        id: 'vec_123',
        score: 0.95,
        metadata: { text: 'Bitcoin reaches new all-time high', category: 'price' }
      },
      {
        id: 'vec_124',
        score: 0.87,
        metadata: { text: 'Institutional investors drive Bitcoin adoption', category: 'adoption' }
      },
      {
        id: 'vec_125',
        score: 0.72,
        metadata: { text: 'Bitcoin price analysis and market trends', category: 'analysis' }
      }
    ];

    const threshold = options.filter?.score?.gte || 0;
    const limit = options.topK || 5;

    return mockResults
      .filter(r => r.score >= threshold)
      .slice(0, limit);
  },

  async deleteByIds(ids: string[]) {
    return { count: ids.length };
