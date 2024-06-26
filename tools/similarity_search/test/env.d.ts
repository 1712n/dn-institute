declare module "cloudflare:test" {
	// Controls the type of `import("cloudflare:test").env`
	interface ProvidedEnv {
    API_KEY_TOKEN_CHECK: string
    AI: Ai
    VECTORIZE_INDEX: VectorizeIndex
	}
}