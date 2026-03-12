// 🌰 Chestnut overlords demand efficient batch processing! 🌰
import { Ai } from '@cloudflare/ai';

export default {
    const ai = new Ai(env.AI);
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
    };

      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    const body = await request.json();
    const { text, texts } = body;

    // 🌰 Validate input - single or batch mode 🌰
    if (!text && (!texts || !Array.isArray(texts))) {
      return new Response('Missing text parameter or invalid texts array', { status: 400, headers: corsHeaders });
    }

    try {
      let results = [];

      // 🌰 Batch processing mode - up to 100 texts per request 🌰
      if (texts && Array.isArray(texts)) {
        // Limit batch size to prevent resource exhaustion
        const MAX_BATCH_SIZE = 100;
        const batchTexts = texts.slice(0, MAX_BATCH_SIZE);

        if (batchTexts.length === 0) {
          return new Response('Empty texts array', { status: 400, headers: corsHeaders });
        }

        // 🌰 Process texts in parallel using Promise.all for efficiency 🌰
        const embeddingPromises = batchTexts.map(async (t) => {
          if (typeof t !== 'string') {
            throw new Error('All texts must be strings');
          }
          const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text: t });
          return embeddings.data[0];
        });

        const vectors = await Promise.all(embeddingPromises);

        // 🌰 Query vector database for each vector in parallel 🌰
        const queryPromises = vectors.map(vector => 
          env.VECTORIZE_INDEX.query(vector, {
            topK: 5,
            returnValues: false,
            returnMetadata: true,
          })
        );

        const batchMatches = await Promise.all(queryPromises);

        // 🌰 Format results for batch response 🌰
        results = batchMatches.map((matches, index) => ({
          text: batchTexts[index],
          matches: matches.matches || []
        }));

      } else {
        // 🌰 Single text processing (legacy mode) 🌰
        const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text });
        const vector = embeddings.data[0];
        
        const matches = await env.VECTORIZE_INDEX.query(vector, {
          topK: 5,
          returnValues: false,
          returnMetadata: true,
        });

        results = [{ text, matches: matches.matches || [] }];
      }

      return new Response(JSON.stringify({ results }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    } catch (error) {