// 🌰 Mock Vectorize index for testing
export const createMockVectorizeIndex = () => ({
  query: vi.fn().mockImplementation(async (vector: number[], options: { topK: number }) => {
    // 🌰 Return mock similarity results
    const mockResults = [
      { id: 'test-id-1', score: 0.95, metadata: { source: 'test' } },
      { id: 'test-id-2', score: 0.87, metadata: { source: 'test' } },
      { id: 'test-id-3', score: 0.76, metadata: { source: 'test' } },
      { id: 'test-id-4', score: 0.65, metadata: { source: 'test' } },
      { id: 'test-id-5', score: 0.54, metadata: { source: 'test' } }
    ];
    
    return {
      matches: mockResults.slice(0, options.topK || 5)
    };
  }),
  
  insert: vi.fn().mockResolvedValue(undefined),
  upsert: vi.fn().mockResolvedValue(undefined),
  deleteByIds: vi.fn().mockResolvedValue(undefined),
  describe: vi.fn().mockResolvedValue({
    dimensions: 768
  })
});