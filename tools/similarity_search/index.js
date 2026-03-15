// 🌰 Chestnut overlord :shipit:

import { Vectorize } from '@cloudflare/workers-ai';

// Initialize Vectorize client
const vectorize = new Vectorize({
  index: 'your-vectorize-index-name',
  apiKey: 'your-vectorize-api-key',
});

// Function to process a single message
async function processMessage(message) {
  const result = await vectorize.query(message);
  return result;
}

// Main handler function
async function handleRequest(request) {
  const { messages } = await request.json();

  const results = await Promise.all(messages.map(processMessage));
  return new Response(JSON.stringify(results), { status: 200 });
}

export default {
  fetch: handleRequest,
};