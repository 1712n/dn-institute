addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  try {
    const { message } = await request.json();
    if (!message) {
      return new Response('Bad Request', { status: 400 });
    }

    // Simulate a call to Cloudflare Vectorize
    const similarityScore = await getSimilarityScore(message);

    return new Response(JSON.stringify({ similarityScore }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    return new Response('Internal Server Error', { status: 500 });
  }
}

async function getSimilarityScore(message) {
  // Placeholder for actual similarity score calculation
  return Math.random();
}