import { Vectorize } from '@cloudflare/workers-ai';

async function processBatch(messages) {
  const vectorize = new Vectorize('your-vectorize-binding-name');
  const results = await Promise.all(messages.map(async (message) => {
    const response = await vectorize.query({
      vector: await vectorize.embed(message),
      topK: 1,
      returnVectors: false,
    });
    return response.matches[0] || null;
  }));
  return results;
}

export default {
  async fetch(request, env, ctx) {
    if (request.method !== 'POST') {
      return new Response('Invalid request body', { status: 400 });
    }

    if (Array.isArray(body.messages)) {
      const batchResults = await processBatch(body.messages);
      return new Response(JSON.stringify(batchResults), { status: 200 });
    } else {
      const vectorize = new Vectorize('your-vectorize-binding-name');
      const response = await vectorize.query({
        vector: await vectorize.embed(body.message),
        topK: 1,
        returnVectors: false,
      });
      return new Response(JSON.stringify(response.matches[0] || null), { status: 200 });
    }
  },
};