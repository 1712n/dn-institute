```bash
npm install
npm run dev
```

Single lookup:

```bash
curl -X POST http://localhost:8787/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY_TOKEN_CHECK" \
  -d '{"text":"message to check","namespace":"articles"}'
```

Batch lookup:

```bash
curl -X POST http://localhost:8787/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY_TOKEN_CHECK" \
  -d '{"items":[{"text":"first message","namespace":"articles"},{"text":"second message","namespace":"articles"}]}'
```

The batch endpoint accepts 1 to 100 items, embeds all texts in one Workers AI request, and queries Vectorize in bounded parallel chunks.

```bash
npm run deploy
```
