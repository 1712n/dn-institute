import { vi } from 'vitest';

// 🌰 Mock Cloudflare AI and Vectorize services
vi.mock('@cloudflare/ai', () => ({
  Ai: vi.fn().mockImplementation(() => ({
    run: vi.fn().mockResolvedValue({
      data: [[0.1, 0.2, 0.3, 0.4, 0.5]],
    }),
  })),
}));

vi.mock('@cloudflare/workers-types', () => ({
  VectorizeIndex: vi.fn().mockImplementation(() => ({
    query: vi.fn().mockResolvedValue({
      matches: [
        { id: '1', score: 0.95, metadata: { text: 'similar message 1' } },
        { id: '2', score: 0.87, metadata: { text: 'similar message 2' } },
        { id: '3', score: 0.82, metadata: { text: 'similar message 3' } },
      ],
    }),
  })),
}));