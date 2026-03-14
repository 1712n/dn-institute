import { getVectorDatabase } from 'cloudflare-vectorize';

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
    return new Response('Invalid message', { status: 400 });
  }

  const vectorDatabase = getVectorDatabase('your-namespace-id');
  const results = await vectorDatabase.query(message, { topK: 1 });

  return new Response(JSON.stringify({ similarity: results[0].similarity }), { status: 200 });
}

export default { fetch: handleRequest };