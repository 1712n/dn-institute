import { search } from './vectorize.js';

export async function handleRequest(request) {
  try {
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }
      return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400 });
    }

    if (!data || !data.message) {
      return new Response(JSON.stringify({ error: 'Message field is required' }), { status: 400 });
    }

    const similarityScore = await search(data.message);
    return new Response(JSON.stringify({ similarity_score: similarityScore }), { status: 200 });
  } catch (error) {
    console.error('Error handling request:', error);
    return new Response(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
  }
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});