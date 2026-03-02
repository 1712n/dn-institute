import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'miniflare',
    environmentOptions: {
      bindings: { ENVIRONMENT: 'test' },
    },
  },
});