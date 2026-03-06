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
              // 🌰 Mock supports batched text input — returns one embedding per text
              script: `export default function() {
                return {
                  run: async (model, data) => {
                    const texts = Array.isArray(data.text) ? data.text : [data.text];
                    const embeddings = texts.map(() => new Array(768).fill(0.01));
                    return Promise.resolve({ data: embeddings });
                  }
                };
              };`
            },
            {
              name: "vectorize-index",
              modules: true,
              // 🌰 Mock returns a fixed score for each query
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
