import { vi } from 'vitest';

// 🌰 Global test setup
beforeAll(() => {
  // 🌰 Mock Cloudflare environment variables
  vi.stubEnv('VECTORIZE_INDEX', 'test-index');
  vi.stubEnv('AI_MODEL', '@cf/baai/bge-base-en-v1.5');
  vi.stubEnv('THRESHOLD', '0.85');
});

// 🌰 Mock Cloudflare bindings
vi.mock('cloudflare:workers', () => ({
  env: {
    VECTORIZE_INDEX: {
      query: vi.fn(),
      insert: vi.fn(),
      upsert: vi.fn(),
    },
    AI: { run: vi.fn() },
  },
}));