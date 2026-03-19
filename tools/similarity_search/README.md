# Similarity Search API

Cloudflare Worker that looks up incoming messages in a vector database and returns similarity scores.

## Setup

```
npm install
npm run dev
```

## Deploy

```
npm run deploy
```

## API

### Single text (original)

```
POST /
Content-Type: application/json
X-API-Key: <key>

{
  "text": "sample text to check",
  "namespace": "articles"
}
```

Response:
```json
{ "similarity_score": 0.87 }
```

### Batch processing

Process multiple texts in a single request. Texts are grouped by namespace and embeddings are computed in chunks for efficiency.

```
POST /batch
Content-Type: application/json
X-API-Key: <key>

{
  "items": [
    { "text": "first text", "namespace": "articles", "id": "optional-id-1" },
    { "text": "second text", "namespace": "articles" },
    { "text": "third text", "namespace": "attacks" }
  ]
}
```

Response:
```json
{
  "results": [
    { "id": "optional-id-1", "text": "first text", "namespace": "articles", "similarity_score": 0.87 },
    { "text": "second text", "namespace": "articles", "similarity_score": 0.42 },
    { "text": "third text", "namespace": "attacks", "similarity_score": 0.15 }
  ]
}
```

**Limits:**
- Max batch size: 100 items
- Items are processed in embedding chunks of 20 (Cloudflare AI limit)
- Same-namespace items are grouped to optimize vectorize queries

## Tests

```
npm test
```
