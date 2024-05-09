import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: {
          configPath: "./wrangler.toml"
        }
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
        }
      }
    }
  }
});
