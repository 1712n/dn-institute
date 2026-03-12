// 🌰 Global test setup for Similarity Search API tests
import { vi } from 'vitest';

// 🌰 Mock Cloudflare Workers AI
vi.mock('@cloudflare/workers-ai', () => ({
  Ai: vi.fn().mockImplementation(() => ({
    run: vi.fn().mockImplementation(async (model: string, input: any) => {
      // 🌰 Return mock embedding vector
      return {
        data: Array.from({ length: 768 }, () => Math.random()),
        shape: [768]
      };
    })
  }))
}));