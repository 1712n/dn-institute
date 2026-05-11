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
                  async run(model, data) {
                    return { data: [new Array(768).fill(0.1)] }
                  }
                }
              }`
            },
            {
              name: "vectorize-index",
              modules: true,
              script: `export default function() {
                return {
                  async query(vectorData, options) {
                    if (options.namespace === "empty-namespace") {
                      return { matches: [] }
                    }
                    return { matches: [{ score: 0.95 }] }
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
