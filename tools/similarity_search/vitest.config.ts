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
                  run: async (model, input) => {
                    const texts = Array.isArray(input.text) ? input.text : [input.text]
                    const vectors = texts.map((t, i) => {
                      const vec = new Array(768)
                      for (let j = 0; j < 768; j++) {
                        vec[j] = Math.sin(i + j * 0.01) * 0.1
                      }
                      return vec
                    })
                    return { shape: [texts.length, 768], data: vectors }
                  }
                }
              }`
            },
            {
              name: "vectorize-index",
              modules: true,
              script: `export default function() {
                return {
                  query: async (vector, options) => {
                    if (options && options.namespace === "empty-ns") {
                      return { count: 0, matches: [] }
                    }
                    return {
                      count: 1,
                      matches: [{ id: "vec-1", score: 0.5678 }]
                    }
                  }
                }
              }`
            }
          ]
        }
      }
    }
  }
})
