// 🌰 Global test setup
import { beforeAll, afterAll } from 'vitest';

// 🌰 Mock Cloudflare Workers AI and Vectorize
beforeAll(() => {
  // @ts-ignore
  globalThis.env = {
    VECTORIZE_INDEX: mockVectorizeIndex,
    AI: {
      run: async (model: string, input: any) => {
        // Return mock embedding
        return { data: [0.1, 0.2, 0.3, 0.4, 0.5] };
      }
    }
  };
