// 🌰 Test fixtures for similarity search API

export const testMessages = {
  cryptoRelated: [
    'Bitcoin price surges past $50,000 as institutional investors show renewed interest',
    'Ethereum 2.0 staking rewards reach all-time high',
    'DeFi protocol suffers $10M exploit due to smart contract vulnerability',
    'Central bank digital currencies gaining traction worldwide'
  ],
  blockchainTech: [
    'New consensus mechanism promises 100x faster transaction speeds',
    'Layer 2 scaling solutions see massive adoption',
    'Cross-chain bridge technology enables seamless asset transfers',
    'Zero-knowledge proofs revolutionize privacy in blockchain'
  ],
  unrelatedContent: [
    'Local football team wins championship after 20 years',
    'New restaurant opens downtown serving fusion cuisine',
    'Weather forecast predicts sunny skies for the weekend',
    'Technology conference announces keynote speakers'
  ]
};

export const expectedVectors = {
  crypto: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
  blockchain: [0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.05],
  unrelated: [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]
};

export const mockVectorMatches = {
  highSimilarity: [
    { id: 'vec1', score: 0.95, metadata: { category: 'crypto', source: 'news' } },
    { id: 'vec2', score: 0.92, metadata: { category: 'crypto', source: 'blog' } }
  ],
  mediumSimilarity: [
    { id: 'vec3', score: 0.75, metadata: { category: 'blockchain', source: 'tech' } },
    { id: 'vec4', score: 0.68, metadata: { category: 'finance', source: 'report' } }
  ],
  lowSimilarity: [
    { id: 'vec5', score: 0.25, metadata: { category: 'sports', source: 'news' } },
    { id: 'vec6', score: 0.15, metadata: { category: 'entertainment', source: 'blog' } }
  ]
};