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
                      throw new Error("unexpected model");
                    }

                    if (!Array.isArray(data.text) || typeof data.text[0] !== "string") {
                      throw new Error("unexpected AI input");
                    }

                    if (data.text[0] === "trigger-workers-ai-failure") {
                      throw new Error("simulated Workers AI failure");
                    }

                    return Promise.resolve({ data: [[0.11, 0.22, 0.33]] });
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
                      throw new Error("unexpected vector data");
                    }

                    if (options.topK !== 1) {
                      throw new Error("unexpected topK");
                    }

                    if (options.namespace === "empty-namespace") {
                      return Promise.resolve({ matches: [] });
                    }

                    if (options.namespace === "vectorize-failure") {
                      throw new Error("simulated Vectorize failure");
                    }

                    const score = options.namespace === "security-incidents" ? 0.8765 : 0.4321;
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
