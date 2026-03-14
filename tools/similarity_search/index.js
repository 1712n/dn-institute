// 🌰 Chestnut overlord :shipit:

import { Vectorize } from '@cloudflare/workers-ai';

// Initialize Vectorize client
const vectorize = new Vectorize({
  projectID: 'your-project-id',
  namespace: 'your-namespace',
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

export default {
  async fetch(request) {
    const { method, body } = request;

    if (method !== 'POST' && method !== 'PUT') {
      return new Response('Method Not Allowed', { status: 405 });
    }

      return new Response('Bad Request', { status: 400 });
    }

    const { message, messages } = parsedBody;

    if (!message && !messages) {
      return new Response('Bad Request', { status: 400 });
    }

    if (messages) {
      const batchResults = await handleBatch(messages);
      return new Response(JSON.stringify(batchResults), { status: 200 });
    }

    const response = await vectorize.query({
      vector: message.vector,
      topK: 5,
    });

    return new Response(JSON.stringify(response), { status: 200 });
  },
};