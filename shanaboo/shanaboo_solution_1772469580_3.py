import { vi } from 'vitest';

// 🌰 Global test setup
vi.mock('cloudflare:test', () => ({
  env: {},
  createExecutionContext: vi.fn(),
  waitOnExecutionContext: vi.fn()
}));