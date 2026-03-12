export async function handleRequest(request) {
  // Mock implementation for testing purposes
  const { message } = await request.json();
  const similarityScore = await getSimilarityScore(message);
  return new Response(JSON.stringify({ similarityScore }), {
    headers: { 'Content-Type': 'application/json' },
  });
}

async function getSimilarityScore(message) {
  // Mock similarity score calculation
  return Math.random();
}