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
              script: `
                const EXPECTED_MODEL = "@cf/baai/bge-base-en-v1.5";
                const VECTOR_DIM = 768;
                const MOCK_VECTOR = Array.from({ length: VECTOR_DIM }, (_, i) => (i % 100) / 100);
                export default function() {
                  return {
                    run: async (model, input) => {
                      if (model !== EXPECTED_MODEL) {
                        throw new Error("Unexpected model: " + model);
                      }
                      if (!Array.isArray(input.text) || input.text.length !== 1 || typeof input.text[0] !== "string") {
                        throw new Error("Expected input.text to be a single-element string array");
                      }
                      return Promise.resolve({ data: [MOCK_VECTOR] });
                    }
                  };
                };`
            },
            {
              name: "vectorize-index",
              modules: true,
              script: `
                const EXPECTED_VECTOR_DIM = 768;
                export default function() {
                  return {
                    query: async (vectorData, options) => {
                      if (!Array.isArray(vectorData) || vectorData.length !== EXPECTED_VECTOR_DIM) {
                        throw new Error("Expected 768-dim vector, got: " + (Array.isArray(vectorData) ? vectorData.length : typeof vectorData));
                      }
                      if (options.topK !== 1) {
                        throw new Error("Expected topK=1, got: " + options.topK);
                      }
                      const score = 0.5678;
                      return Promise.resolve({ matches: [{ id: "doc-1", score }] });
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
