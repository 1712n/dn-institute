import { getVectorDatabase } from 'cloudflare-vectorize';

export async function handleRequest(request) {
try {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
    return new Response('Invalid JSON body', { status: 400 });
  }

  const { message } = body;
  if (!message) {
    return new Response('Message is required', { status: 400 });
  }
  return new Response(JSON.stringify({ similarity: results[0].similarity, id: results[0].id }), {
    headers: { 'Content-Type': 'application/json' },
  });
} catch (error) {
  return new Response('Internal Server Error', { status: 500 });
}
}