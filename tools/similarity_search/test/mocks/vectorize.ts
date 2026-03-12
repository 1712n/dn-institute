// 🌰 Mock Vectorize index for testing
export class MockVectorizeIndex {
  private vectors: Map<string, any> = new Map();

  async query(vector: number[], options?: { topK?: number; returnValues?: boolean; returnMetadata?: boolean }) {
    const topK = options?.topK || 10;
    
    // 🌰 Return mock similarity results
    const mockResults = [
      { id: 'vec1', score: 0.95, metadata: { text: 'highly similar content' } },
      { id: 'vec2', score: 0.87, metadata: { text: 'moderately similar content' } },
      { id: 'vec3', score: 0.72, metadata: { text: 'somewhat similar content' } },
      { id: 'vec4', score: 0.65, metadata: { text: 'low similarity content' } },
    ];

    return {
      matches: mockResults.slice(0, topK),
      count: Math.min(topK, mockResults.length),
    };
  }

  async upsert(vectors: any[]) {
    vectors.forEach(vec => {
      this.vectors.set(vec.id, vec);
    });
    return {
      ids: vectors.map(v => v.id),
    };
  }
}