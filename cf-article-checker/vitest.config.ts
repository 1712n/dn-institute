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
            BRAVE_API_KEY: "test-brave-key",
            REVIEWERS: "testuser,anotherreviewer",
            ANTHROPIC_MODEL: "claude-3-5-sonnet-20241022",
            ANTHROPIC_MAX_TOKENS: "4000",
          },
          // Mock external API calls
          serviceBindings: {
            async MOCK_AI() {
              return new Response(
                JSON.stringify({
                  content: [{ type: "text", text: "<answer>Test review</answer>" }],
                  stop_reason: "end_turn",
                  stop_sequence: null,
                }),
                { status: 200, headers: { "Content-Type": "application/json" } }
              );
            },
          },
        },
      },
    },
  },
});
