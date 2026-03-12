// 🌰 Test setup utilities for similarity search integration tests

export const mockVectorizeResponse = {
  matches: [
    {
      id: "test-1",
      score: 0.85,
      metadata: { text: "Bitcoin price reaches new all-time high amid institutional adoption" }
    },
    {
      id: "test-2", 
      score: 0.72,
      metadata: { text: "Ethereum 2.0 staking rewards increase significantly" }
    }
  ]
};