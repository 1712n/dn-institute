import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config"

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: {
          configPath: "./wrangler.toml"
        },
        miniflare: {
          bindings: {
            API_KEY_TOKEN_CHECK: "test-api-key"
          },
          wrappedBindings: {
            AI: {
              scriptName: "workers-ai"
            },
            VECTORIZE_INDEX: {
              scriptName: "vectorize-index"
            }
          },
          workers: [
            {
              name: "workers-ai",
              modules: true,
              script: `export default function() {
                return {
                  run: async (model, data) => {
                    const text = data.text?.[0];
                    if (text === "trigger-ai-error") {
                      throw new Error("AI binding unavailable");
                    }
                    if (text === "empty-embedding") {
                      return Promise.resolve({ data: [] });
                    }
                    if (text === "invalid-embedding") {
                      return Promise.resolve({ data: [[0.1, "not-a-number", 0.3]] });
                    }
                    return Promise.resolve({ data: [[0.1, 0.2, 0.3]] });
                  }
                };
              };`
            },
            {
              name: "vectorize-index",
              modules: true,
              script: `export default function() {
                return {
                  query: async (vectorData, options) => {
                    if (options.namespace === "trigger-vectorize-error") {
                      throw new Error("Vectorize query failed");
                    }
                    if (!Array.isArray(vectorData)) {
                      throw new Error("Expected embedding vector");
                    }
                    if (options.namespace === "no-match") {
                      return Promise.resolve({ matches: [] });
                    }
                    const score = 0.5678;
                    return Promise.resolve({ matches: [{ score }] });
                  }
                };
              };`
            }
          ]
        }
      }
    }
  }
})
