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
                      throw new Error("Unexpected model");
                    }
                    const text = data?.text?.[0];
                    if (text === "trigger-ai-error") {
                      throw new Error("Workers AI unavailable");
                    }
                    if (text === "trigger-invalid-embedding") {
                      return Promise.resolve({ data: [] });
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
                    if (!Array.isArray(vectorData)) {
                      throw new Error("Vectorize received invalid vector data");
                    }
                    if (options?.namespace === "vectorize-error") {
                      throw new Error("Vectorize unavailable");
                    }
                    if (options?.namespace === "no-matches") {
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
