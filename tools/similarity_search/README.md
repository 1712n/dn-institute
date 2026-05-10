```
npm install
npm run dev
```

```
npm run deploy
```

## Local integration tests

Run the Cloudflare Worker integration tests from this directory:

```
npm install
npm test -- --run
```

The test suite uses `@cloudflare/vitest-pool-workers` with mocked Workers AI
and Vectorize bindings. The tests cover:

- API key authentication through `X-API-Key`.
- Valid `POST /` requests returning the top Vectorize similarity score.
- Empty Vectorize matches returning `similarity_score: 0`.
- Malformed JSON and invalid request shapes returning `400`.
- Missing Workers AI embeddings returning `502` before Vectorize is queried.
