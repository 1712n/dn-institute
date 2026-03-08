import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: {
          configPath: "./wrangler.toml",
        },
        miniflare: {
          bindings: {
            GITHUB_TOKEN: "test-github-token",
            ANTHROPIC_API_KEY: "test-anthropic-key",
            GITHUB_WEBHOOK_SECRET: "test-webhook-secret",
            BRAVE_API_KEY: "test-brave-key",
            ANTHROPIC_MODEL: "claude-3-opus-20240229",
            ANTHROPIC_MAX_TOKENS: "4000",
          },
        },
      },
    },
  },
});
