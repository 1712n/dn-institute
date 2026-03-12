import { vi } from 'vitest';

// 🌰 Mock Cloudflare Workers AI and Vectorize bindings
vi.mock('cloudflare:workers', () => ({
  env: {
    VECTORIZE_INDEX: {
      query: vi.fn().mockImplementation(async (vector: number[], options: any) => {
        // 🌰 Return mock similarity results
        return {
          matches: Array.from({ length: Math.min(options.topK || 5, 3) }, (_, i) => ({
            id: `test-id-${i}`,
            score: 0.9 - (i * 0.1),
          })),
        };
      }),
    },
    AI: {
      run: vi.fn().mockResolvedValue([0.1, 0.2, 0.3, 0.4, 0.5]), // 🌰 Mock embedding
    },
  },
}));