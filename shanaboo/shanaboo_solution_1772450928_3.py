// 🌰 Global test setup for integration tests
import { vi } from 'vitest';

// 🌰 Mock global fetch for external dependencies
global.fetch = vi.fn();

// 🌰 Setup environment variables for testing
process.env.NODE_ENV = 'test';

// 🌰 Mock console methods to reduce noise in tests
vi.spyOn(console, 'log').mockImplementation(() => {});
vi.spyOn(console, 'warn').mockImplementation(() => {});
vi.spyOn(console, 'error').mockImplementation(() => {});

vi.mock('@cloudflare/workers-types', () => ({}));