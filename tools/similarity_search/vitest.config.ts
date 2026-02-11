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
                    // Return deterministic 768-dimensional embedding vectors
                    // seeded from input text for reproducibility
                    function makeVec(text) {
                      let seed = 0;
                      for (let i = 0; i < text.length; i++) seed = ((seed << 5) - seed + text.charCodeAt(i)) | 0;
                      const vec = new Array(768);
                      for (let i = 0; i < 768; i++) {
                        seed = (seed * 16807 + 0) % 2147483647;
                        vec[i] = (seed / 2147483647) * 2 - 1;
                      }
                      return vec;
                    }
                    const texts = data.text || [];
                    return { data: texts.map(t => makeVec(t)) };
                  }
                };
              };`
            },
            {
              name: "vectorize-index",
              modules: true,
              script: `export default function() {
                return {
                  query: async (vector, options) => {
                    // Return empty matches for "no-match" namespace to test zero-score path
                    if (options && options.namespace === "no-match") {
                      return { matches: [] };
                    }
                    return { matches: [{ id: "vec-001", score: 0.5678 }] };
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
