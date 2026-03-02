// 🌰 Chestnut-powered similarity search with batch processing capabilities
export interface Env {
  AI: any;
  VECTORIZE_INDEX: any;
  score: number;
}

export interface BatchQueryResult {
  message: string;
  results: QueryResult[];
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
    }

    const url = new URL(request.url);
    
    // 🌰 Route handling for both single and batch processing
    if (url.pathname === '/query') {
      return handleQuery(request, env);
    } else if (url.pathname === '/batch') {
  },
};

// 🌰 Single message query handler
async function handleQuery(request: Request, env: Env): Promise<Response> {
  const { message, topK = 5 } = await request.json();
  
    results: matches.matches,
  });
}

// 🌰 Batch message processing handler - optimized for Cloudflare Workers
async function handleBatchQuery(request: Request, env: Env): Promise<Response> {
  const { messages, topK = 5 } = await request.json();
  
  if (!Array.isArray(messages)) {
    return new Response(JSON.stringify({ error: 'Messages must be an array' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // 🌰 Cloudflare Workers limit: enforce reasonable batch size to prevent timeouts
  const MAX_BATCH_SIZE = 100;
  if (messages.length > MAX_BATCH_SIZE) {
    return new Response(JSON.stringify({ 
      error: `Batch size exceeds limit of ${MAX_BATCH_SIZE} messages` 
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // 🌰 Process all messages concurrently using Promise.all for optimal performance
  const batchPromises = messages.map(async (msg: string) => {
    try {
      const embeddings = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
        text: [msg],
      });

      const matches = await env.VECTORIZE_INDEX.query(embeddings.data[0], {
        topK: Math.min(topK, 10), // 🌰 Cap topK to prevent excessive vector lookups
        returnValues: true,
        returnMetadata: true,
      });

      return {
        message: msg,
        results: matches.matches,
      };
    } catch (error) {
      // 🌰 Graceful error handling per message - don't fail entire batch
      return {
        message: msg,
        error: 'Failed to process message',
        results: [],
      };
    }
  });

  const results = await Promise.all(batchPromises);

  return new Response(JSON.stringify({ 
    results,
    processedCount: results.length 
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
}