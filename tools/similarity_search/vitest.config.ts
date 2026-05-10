import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config"

// 🌰 Vitest pool config — mocks AI embeddings and Vectorize for deterministic integration tests
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
              // 🌰 AI mock — validates model name and input shape, returns a fixed 3-dim embedding
              name: "workers-ai",
              modules: true,
              script: `export default function() {
                return {
                  run: async (model, data) => {
                    if (model !== "@cf/baai/bge-base-en-v1.5") {
                      throw new Error("unexpected model: " + model);
                    }
                    if (!Array.isArray(data.text) || typeof data.text[0] !== "string") {
                      throw new Error("unexpected AI input shape");
                    }
                    return Promise.resolve({ data: [[0.11, 0.22, 0.33]] });
                  }
                };
              };`
            },
            {
              // 🌰 Vectorize mock — asserts vector shape, topK, and namespace; returns namespace-specific scores
              name: "vectorize-index",
              modules: true,
              script: `export default function() {
                return {
                  query: async (vectorData, options) => {
                    if (!Array.isArray(vectorData) || vectorData.length !== 3) {
                      throw new Error("unexpected vector shape: length=" + vectorData.length);
                    }
                    if (options.topK !== 1) {
                      throw new Error("unexpected topK: " + options.topK);
                    }
                    if (options.namespace === "empty-namespace") {
                      return Promise.resolve({ matches: [] });
                    }
                    if (options.namespace === "unicode-smoke") {
                      return Promise.resolve({ matches: [{ score: 0.4321 }] });
                    }
                    if (options.namespace === "near-duplicate") {
                      return Promise.resolve({ matches: [{ score: 0.9876 }] });
                    }
                    return Promise.resolve({ matches: [{ score: 0.8765 }] });
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
