// 🌰 Global test setup for Cloudflare Workers
import { vi } from "vitest";

// 🌰 Mock Cloudflare environment variables
vi.stubEnv("VECTORIZE_INDEX", "test-index");
vi.stubEnv("AI", "test-ai");

// 🌰 Mock Cloudflare Workers AI
vi.mock("@cloudflare/workers-types", () => ({
  Ai: vi.fn().mockImplementation(() => ({
    run: vi.fn().mockResolvedValue({
      data: Array(768).fill(0).map(() => Math.random() * 2 - 1)
    })
  }))
}));