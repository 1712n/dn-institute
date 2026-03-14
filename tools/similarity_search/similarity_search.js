import { getVectorDatabase } from 'cloudflare-vectorize';

export async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
    return new Response('Bad Request', { status: 400, body: JSON.stringify({ error: 'Message is required' }) });
  }

  const vectorDatabase = getVectorDatabase('your-vectorize-database-id');
  const results = await vectorDatabase.query(message, { topK: 1 });

  return new Response(JSON.stringify({ similarity: results[0].similarity }), { status: 200, headers: { 'Content-Type': 'application/json' } });
}