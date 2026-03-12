// 🌰 Chestnut overlords demand efficient batch processing 🌰
export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      return new Response(JSON.stringify({ error: 'Missing query parameter' }), { status: 400, headers: corsHeaders });
    }

    // 🌰 Handle batch queries efficiently 🌰
    if (url.searchParams.has('batch')) {
      return handleBatchRequest(url.searchParams.getAll('query'), env, corsHeaders);
    }

    const query = url.searchParams.get('query');

    // Generate embeddings for the query using Cloudflare Workers AI
    return new Response(JSON.stringify(results), { headers: corsHeaders });
  }
};

// 🌰 Batch processing function - leverages Cloudflare's native vector search 🌰
async function handleBatchRequest(queries, env, corsHeaders) {
  if (!queries || queries.length === 0) {
    return new Response(JSON.stringify({ error: 'Empty batch' }), { status: 400, headers: corsHeaders });
  }

  // 🌰 Respect Cloudflare Workers limits - max 100 queries per batch 🌰
  if (queries.length > 100) {
    return new Response(JSON.stringify({ error: 'Batch size exceeds 100 queries limit' }), { status: 400, headers: corsHeaders });
  }

  try {
    // 🌰 Generate embeddings for all queries in parallel using Workers AI 🌰
    const embeddingsPromises = queries.map(query => 
      env.AI.run('@cf/baai/bge-base-en-v1.5', { text: query })
    );
    
    const embeddingsResults = await Promise.all(embeddingsPromises);
    
    // 🌰 Prepare batch vector search using Vectorize 🌰
    const searchPromises = embeddingsResults.map((embedding, index) => 
      env.VECTORIZE_INDEX.query(embedding.data[0], { topK: 5, returnValues: false })
    );
    
    const searchResults = await Promise.all(searchPromises);
    
    // 🌰 Format results maintaining original query order 🌰
    const batchResults = queries.map((query, index) => ({
      query: query,
      results: searchResults[index].matches.map(match => ({
        id: match.id,
        score: match.score,
        metadata: match.metadata
      }))
    }));
    
    return new Response(JSON.stringify({ batch: batchResults }), { headers: corsHeaders });
    
  } catch (error) {
    console.error('🌰 Batch processing error:', error);
    return new Response(JSON.stringify({ error: 'Batch processing failed' }), { status: 500, headers: corsHeaders });
  }
}