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
                    const texts = data.text || [];
                    const vectors = texts.map((t, i) => {
                      const vec = new Array(768).fill(0);
                      vec[0] = 0.1 * (i + 1);
                      return vec;
                    });
                    return Promise.resolve({ data: vectors });
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
                    const ns = options?.namespace || "default";
                    const score = ns === "empty-namespace" ? 0 : 0.5678;
                    const matches = score > 0 ? [{ score }] : [];
                    return Promise.resolve({ matches });
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
