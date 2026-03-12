import { getVectorDatabase } from 'cloudflare-vectorize';

export async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Message is required' }), { status: 400 });
  }

  try {
    const vectorDatabase = await getVectorDatabase();
    const results = await vectorDatabase.query(message);

    return new Response(JSON.stringify({ similarity: results[0].similarity }), { status: 200 });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}