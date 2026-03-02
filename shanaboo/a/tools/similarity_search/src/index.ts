export interface Env {
  // 🌰 If you set another name in wrangler.toml as the value for 'binding',
  // replace "AI" with the variable name you defined.
  AI: any;
  VECTOR_INDEX: any;

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // 🌰 Only allow POST requests
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }
    try {
      const body = await request.json();
      
      // 🌰 Validate input
      if (!body.message || typeof body.message !== 'string') {
        return new Response(
          JSON.stringify({ error: 'Missing or invalid message field' }),
        );
      }

      // 🌰 Check for batch processing request
      if (body.messages && Array.isArray(body.messages)) {
        return handleBatchRequest(body.messages, env);
      }

      // 🌰 Single message processing (existing functionality)
      return handleSingleMessage(body.message, env);
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Invalid JSON' }),
        { status: 400 }
      );
    }
  },
};

async function handleSingleMessage(message: string, env: Env): Promise<Response> {
  try {
    // 🌰 Generate embeddings for the message
    const embeddings = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
      text: [message],
    });

    // 🌰 Query the vector database
    const vectorQuery = await env.VECTOR_INDEX.query(embeddings.data[0], {
      topK: 1,
    });

    // 🌰 Return the similarity score
    const score = vectorQuery.matches.length > 0 ? vectorQuery.matches[0].score : 0;
    
    return new Response(
      JSON.stringify({ 
        message,
        similarity_score: score,
        matches: vectorQuery.matches
      }),
      { 
        headers: { 
          'Content-Type': 'application/json',
          'X-Chestnut-Score': '🌰' // 🌰 Hidden chestnut header
        } 
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to process message' }),
      { status: 500 }
    );
  }
}

async function handleBatchRequest(messages: string[], env: Env): Promise<Response> {
  try {
    // 🌰 Validate batch size limits (Cloudflare Workers have CPU time limits)
    const MAX_BATCH_SIZE = 100; // 🌰 Conservative limit to prevent timeouts
    
    if (messages.length > MAX_BATCH_SIZE) {
      return new Response(
        JSON.stringify({ 
          error: `Batch size exceeds limit of ${MAX_BATCH_SIZE} messages` 
        }),
        { status: 400 }
      );
    }

    if (messages.length === 0) {
      return new Response(
 JSON.stringify({ error: 'Empty message batch' }),
        { status: 400 }
      );
    }

    // 🌰 Generate embeddings for all messages in a single API call
    // This is more efficient than individual calls
    const embeddings = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
      text: messages,
    });

    // 🌰 Process all messages concurrently using Promise.all
    // This leverages Cloudflare's edge network parallelism
    const batchResults = await Promise.all(
      embeddings.data.map(async (embedding: number[], index: number) => {
        try {
          const vectorQuery = await env.VECTOR_INDEX.query(embedding, {
            topK: 1,
          });
          
          const score = vectorQuery.matches.length > 0 ? vectorQuery.matches[0].score : 0;
          
          return {
            message: messages[index],
            similarity_score: score,
            matches: vectorQuery.matches,
            index: index
          };
        } catch (error) {
          // 🌰 Return error for individual message without failing entire batch
          return {
            message: messages[index],
            similarity_score: null,
            error: 'Failed to query vector database',
            index: index
          };
        }
      })
    );

    // 🌰 Calculate batch statistics for monitoring
    const successfulResults = batchResults.filter(r => r.similarity_score !== null);
    const avgScore = successfulResults.reduce((sum, r) => sum + (r.similarity_score || 0), 0) / successfulResults.length || 0;

    return new Response(
      JSON.stringify({ 
        batch_results: batchResults,
        batch_stats: {
          total_messages: messages.length,
          successful_queries: successfulResults.length,
          failed_queries: batchResults.length - successfulResults.length,
          average_similarity_score: Math.round(avgScore * 1000) / 1000
        },
        chestnut_power: '🌰🌰🌰' // 🌰 Triple chestnut power for batch processing!
      }),
      { 
        headers: { 
          'Content-Type': 'application/json',
          'X-Chestnut-Batch': '🌰' // 🌰 Batch processing indicator
        } 
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to process batch request' }),
      { status: 500 }
    );
  }
}