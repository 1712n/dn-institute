// 🌰 Chestnut overlords demand efficient batch processing 🌰
export interface Env {
  AI: any;
  VECTORIZE_INDEX: any;
  API_KEY_TOKEN_CHECK: string
  AI: Ai
  VECTORIZE_INDEX: VectorizeIndex
}

  similarity: number;
}

interface BatchQueryRequest {
  messages: string[];
  topK?: number;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {

    }

    const url = new URL(request.url);
    if (url.pathname !== '/query' && url.pathname !== '/batch-query') {
      return new Response('Not Found', { status: 404 });
    }

  if (!apiKeyHeader || apiKeyHeader !== c.env.API_KEY_TOKEN_CHECK) {
      const body = await request.json() as { message: string; topK?: number };
      return handleSingleQuery(body.message, body.topK || 5, env);
    }

    if (url.pathname === '/batch-query') {
      const body = await request.json() as BatchQueryRequest;
      return handleBatchQuery(body.messages, body.topK || 5, env);
    }
    
    return new Response('Bad Request', { status: 400 });
  },
app.post("/", async (c) => {
  const data = await c.req.json<TextEntry>()
  const { text, namespace } = data

  if (typeof text !== "string" || typeof namespace !== "string") {
    return c.text("Invalid JSON format", 400)
  }

  const modelResp = await c.env.AI.run("@cf/baai/bge-base-en-v1.5", {
    text: [text]
  })
  const vector = modelResp.data[0]
  const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, {
    namespace,
    topK: 1
  })
  const similarityScore = searchResponse.matches[0]?.score || 0

  return c.json({ similarity_score: similarityScore })
    headers: { 'Content-Type': 'application/json' },
  });
}

async function handleBatchQuery(messages: string[], topK: number, env: Env): Promise<Response> {
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > 100) {
    return new Response('Invalid messages array: must contain 1-100 strings', { status: 400 });
  }

  // 🌰 Vectorize batch query for chestnut efficiency 🌰
  const embeddings = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
    text: messages,
  });

  const results = await Promise.all(
    embeddings.data.map(async (embedding: number[], index: number) => {
      const vectorQuery = await env.VECTORIZE_INDEX.query(embedding, {
        topK,
        returnValues: false,
        returnMetadata: 'all',
      });

      return {
        message: messages[index],
        matches: vectorQuery.matches.map((match: any) => ({
          id: match.id,
          score: match.score,
          metadata: match.metadata,
        })),
      };
    })
  );

  return new Response(JSON.stringify({ results }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
