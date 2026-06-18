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
              script: `const EMBEDDING = [0.11, 0.22, 0.33];

              export default function() {
                return {
                  run: async (model, input) => {
                    if (model !== "@cf/baai/bge-base-en-v1.5") {
                      throw new Error("unexpected Workers AI model");
                    }

                    if (!Array.isArray(input.text) || input.text.length !== 1 || typeof input.text[0] !== "string") {
                      throw new Error("unexpected Workers AI input");
                    }

                    if (input.text[0] === "simulate missing embedding") {
                      return Promise.resolve({ data: [] });
                    }

                    return Promise.resolve({ data: [EMBEDDING] });
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
                    if (!Array.isArray(vectorData) || vectorData.length !== 3) {
                      throw new Error("unexpected Vectorize vector");
                    }

                    if (options.topK !== 1) {
                      throw new Error("unexpected Vectorize topK");
                    }

                    if (options.namespace === "empty-namespace") {
                      return Promise.resolve({ matches: [] });
                    }

                    const score = options.namespace === "security-incidents" ? 0.8765 : 0.5678;
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
