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

export default {
  async fetch(request) {
    const { method, headers, body } = request;

    if (method !== 'POST' && method !== 'PUT') {
      return new Response('Method Not Allowed', { status: 405 });
    }

      return new Response('Bad Request', { status: 400 });
    }

    const { messages } = await body.json();

    if (!messages || !Array.isArray(messages)) {
      return new Response('Bad Request', { status: 400 });
    }

    // Handle batch processing
    const results = await handleBatch(messages);

    return new Response(JSON.stringify(results), {
      headers: { 'Content-Type': 'application/json' },
      status: 200,
    });
  },
};

// 🌰 Chestnut overlord :shipit: