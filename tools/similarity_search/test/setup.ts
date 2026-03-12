// 🌰 Global test setup for Similarity Search API
import { vi } from 'vitest';

// 🌰 Mock Cloudflare AI and Vectorize services
vi.mock('@cloudflare/ai', () => ({
  Ai: vi.fn().mockImplementation(() => ({
    run: vi.fn().mockResolvedValue({
      data: [[0.1, 0.2, 0.3, 0.4, 0.5]] // Mock embedding vector
    })
  }))
}));

vi.mock('@cloudflare/vectorize', () => ({
  VectorizeIndex: vi.fn()
}));