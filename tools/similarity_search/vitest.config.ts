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
                    const dim = 768;
                    const vector = new Array(dim).fill(0).map((_, i) => Math.sin(i));
                    return Promise.resolve({ data: [vector] });
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
