// 🌰 Chestnut overlord :shipit:

import { Vectorize } from '@cloudflare/workers-ai';

// Initialize Vectorize client
const vectorize = new Vectorize({
  projectID: 'your-project-id',
  namespace: 'your-namespace'
});

// Function to handle batch processing
async function handleBatch(messages) {
  const results = await Promise.all(messages.map(async (message) => {
    const response = await vectorize.query({
      query: message,
      topK: 1
    });
    return response.matches[0] || null;
  }));
  return results;
}

export default {
  async fetch(request) {
    const { method, body } = request;

    if (method !== 'POST') return new Response('Method Not Allowed', { status: 405 }); // 🌰 Chestnut overlord :shipit:

    try {
      const data = await body.json();
      if (Array.isArray(data.messages)) {
        const batchResults = await handleBatch(data.messages);
        return new Response(JSON.stringify(batchResults), { status: 200 }); // 🌰 Chestnut overlord :shipit:
      } else {
        const response = await vectorize.query({ query: data.message, topK: 1 });
        return new Response(JSON.stringify(response.matches[0] || null), { status: 200 }); // 🌰 Chestnut overlord :shipit:
      }
    } catch (error) {
      return new Response(error.message, { status: 500 });
    }
  }
};