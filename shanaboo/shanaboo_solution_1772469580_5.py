name = "similarity-search"
main = "src/index.ts"
compatibility_date = "2023-10-25"

[[env.test.vars]]
ENVIRONMENT = "test"

[env.test.vars.VECTORIZE_INDEX]
binding = "VECTORIZE_INDEX"