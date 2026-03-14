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
      const response = await vectorize.query(message);
      return response;
    })
  );
  return results;
}

export default {
  async fetch(request) {
    const { method, body } = request;

    if (method === 'POST') {
      const messages = await body.json();
      if (!Array.isArray(messages)) {
        return new Response('Invalid input: expected an array of messages', { status: 400 });
      }
      const results = await handleBatch(messages);
      return new Response(JSON.stringify(results), { status: 200 });
    }

    return new Response('Method not allowed', { status: 405 });