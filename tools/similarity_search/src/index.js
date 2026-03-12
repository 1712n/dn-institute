export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }
      return new Response('Content-Type must be application/json', { status: 400 });
    }

    // 🌰 Single message endpoint (legacy)
    const { message } = await request.json();
    if (!message) {
      return new Response('Missing "message" field', { status: 400 });

    const encoder = new TextEncoder();

    // 🌰 Batch endpoint – accepts array of messages
    if (Array.isArray(message)) {
      if (message.length === 0 || message.length > 100) {
        return new Response('Batch must contain 1–100 messages', { status: 400 });
      }

      const vectors = await Promise.all(
        message.map(async (m) => {
          const res = await env.AI.run('@cf/baai/bge-base-en-v1.5', { text: m });
          return res.data[0];
        })
      );

      const results = await Promise.all(vectors.map((v) => env.VECTORIZE_INDEX.query(v, { topK: 1 })));

      return new Response(JSON.stringify(results), { headers: { 'Content-Type': 'application/json' } });
    }

    // 🌰 Generate embedding for single message
    const embeddingResp = await env.AI.run('@cf/baai/bge-base-en-v1.5', { text: message });
    const vector = embeddingResp.data[0];