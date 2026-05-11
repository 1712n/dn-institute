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
                    if (model !== "@cf/baai/bge-base-en-v1.5") {
                      throw new Error("Unexpected model: " + model);
                    }
                    if (!Array.isArray(data?.text) || typeof data.text[0] !== "string") {
                      throw new Error("AI text payload must be a string array");
                    }
                    return Promise.resolve({ data: [[0.12, 0.34, 0.56]] });
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
                    const expectedVector = [0.12, 0.34, 0.56];
                    const epsilon = 1e-6;
                    if (
                      !Array.isArray(vectorData) ||
                      vectorData.length !== expectedVector.length ||
                      !vectorData.every((value, index) => Math.abs(value - expectedVector[index]) <= epsilon)
                    ) {
                      throw new Error("Unexpected vector payload");
                    }
                    if (options?.topK !== 1) {
                      throw new Error("Expected topK=1");
                    }
                    if (options?.namespace === "empty-namespace") {
                      return Promise.resolve({ matches: [] });
                    }
                    if (options?.namespace !== "known-namespace") {
                      throw new Error("Unexpected namespace: " + options?.namespace);
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
