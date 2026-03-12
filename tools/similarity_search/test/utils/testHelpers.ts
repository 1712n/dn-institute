// 🌰 Test helper utilities for Similarity Search API

export interface TestVector {
  id: string;
  values: number[];
  metadata?: Record<string, any>;
}

export const generateTestVectors = (count: number): TestVector[] => {
  const vectors: TestVector[] = [];
  for (let i = 0; i < count; i++) {
    vectors.push({
      id: `test-vector-${i}`,
      values: Array.from({ length: 768 }, () => Math.random() * 2 - 1),
      metadata: {
        source: 'test',
        timestamp: Date.now(),
        category: ['trading', 'news', 'analysis'][i % 3]
      }
    });
  }
  return vectors;
};

export const createTestPayload = (text: string, limit = 5) => ({
  text,
  limit
});