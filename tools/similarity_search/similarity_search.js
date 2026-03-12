export async function handleRequest(request) {
try {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
    return new Response('Bad Request', { status: 400 });
  }

  const { message } = await request.json().catch(() => ({ message: null }));

  if (!message) {
    return new Response('Bad Request', { status: 400 });
  const similarityScore = await calculateSimilarity(message);

  return new Response(JSON.stringify({ similarity_score: similarityScore }), {
    headers: { 'Content-Type': 'application/json' },
    status: 200,
  });
} catch (error) {
  return new Response('Internal Server Error', { status: 500 });
}
}