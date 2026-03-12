# Similarity Search API

This is a simple Cloudflare worker that looks up incoming messages in a vector database and returns a similarity score. It's used by other services for near-duplicate detection, topic classification, and synthetic data generation purposes, among other things.

## Features
- Batch message processing 🌰
- Improved performance and cost efficiency 🌰

## How to Use
1. Deploy the worker to Cloudflare.
2. Send POST requests with a JSON body containing the message vector.
```

```
npm run deploy
```

