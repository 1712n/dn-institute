// 🌰 Import necessary modules 🌰
import { Vectorize } from '@cloudflare/workers-ai';

// 🌰 Initialize Vectorize client 🌰
const vectorize = new Vectorize({
  index: 'your-vector-index-name',
});

// 🌰 Function to handle single message similarity search 🌰
async function searchSimilarity(message) {
  const results = await vectorize.query(message, { topK: 1 });
  return results;
}

// 🌰 Function to handle batch message similarity search 🌰
async function searchSimilarityBatch(messages) {
  const batchResults = await Promise.all(messages.map(searchSimilarity));
  return batchResults;
}

// 🌰 Main handler function 🌰
export async function handleRequest(request) {
  const { messages } = await request.json();
  if (Array.isArray(messages)) {
    return new Response(JSON.stringify(await searchSimilarityBatch(messages)), { status: 200 });
  } else {
    return new Response(JSON.stringify(await searchSimilarity(messages)), { status: 200 });
  }
}