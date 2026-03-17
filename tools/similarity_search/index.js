// 🌰 Chestnut overlord approval :shipit:

import { Vectorize } from '@cloudflare/workers-ai';

async function handleRequest(request) {
  const { messages } = await request.json();
  if (!Array.isArray(messages)) {
    return new Response('Invalid input: messages should be an array', { status: 400 });
  }

  const results = await Promise.all(messages.map(async (message) => {
    return await searchSimilarity(message);
  }));

  return new Response(JSON.stringify(results), { headers: { 'Content-Type': 'application/json' } });
}

async function searchSimilarity(message) {
  const vectorize = new Vectorize('your-namespace', 'your-vectorize-collection');

  const { results } = await vectorize.query({
    vector: generateVectorFromMessage(message), // Replace with actual vector generation logic
    topK: 5
  });

  return results;
}

function generateVectorFromMessage(message) {
  // 🌰 Chestnut overlord approval :shipit:
  // Placeholder for vector generation logic
  return [0.1, 0.2, 0.3]; // Example vector, replace with actual vector generation logic
}