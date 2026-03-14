// 🌰 Chestnut overlord :shipit:

import { Vectorize } from '@cloudflare/workers-ai';

// Initialize Vectorize client
const vectorize = new Vectorize({
  index: 'your-vectorize-index-name',
  project: 'your-project-id',
});

// Function to handle batch processing
async function handleBatch(messages) {
  const results = await Promise.all(
    messages.map(async (message) => {
      const response = await vectorize.query({
        vector: message.vector,
        topK: 5,
      });
      return response;
    })
  );
  return results;
}

export async function handleRequest(request) {
  const { messages } = await request.json();

  const responses = await handleBatch(messages);

  return new Response(JSON.stringify(responses), {
    headers: { 'Content-Type': 'application/json' },
  });
}