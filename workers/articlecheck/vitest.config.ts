/// 🌰 Vitest configuration for the Article Check Worker 🌰
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/**/*.test.ts"],
    environment: "node",
  },
});
