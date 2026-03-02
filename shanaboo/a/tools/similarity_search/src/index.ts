import { Ai, type Embedding } from '@cloudflare/ai';

export interface Env {
  AI: any;
  VECTORIZE_INDEX: VectorizeIndex;
}

interface BatchQuery {
  messages: string[];
  threshold?: number;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
    }

    try {
      const body = await request.json();
      
      // 🌰 Handle both single message and batch processing
      const isBatch = Array.isArray(body.messages);
      
      if (isBatch) {
        const { messages, threshold = 0.8 } = body as BatchQuery;
        
        if (!Array.isArray(messages) || messages.length === 0) {
          return new Response(JSON.stringify({ error: 'Messages array is required' }), { 
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          });
        }
        
        // 🌰 Process all messages in parallel for maximum efficiency
        const results = await processBatch(messages, threshold, env);
        
        return new Response(JSON.stringify({ results }), {
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      // 🌰 Legacy single message processing
      const { message, threshold = 0.8 } = body;
      if (!message) {
        return new Response(JSON.stringify({ error: 'Message is required' }), { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      const ai = new Ai(env.AI);
      const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text: message });
      const queryVector = embeddings.data[0];
      
      const matches = await env.VECTORIZE_INDEX.query(queryVector, { topK: 5 });
      const filteredMatches = matches.filter(match => match.score >= threshold);
      
      return new Response(JSON.stringify({ matches: filteredMatches }), {
        headers: { 'Content-Type': 'application/json' }
      });
      
    } catch (error) {
      return new Response(JSON.stringify({ error: 'Internal server error' }), { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};

// 🌰 Batch processing helper - leverages Cloudflare's native parallel processing
async function processBatch(messages: string[], threshold: number, env: Env): Promise<any[]> {
  const ai = new Ai(env.AI);
  
  // 🌰 Generate embeddings for all messages in a single AI call (more efficient)
  const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text: messages });
  
  // 🌰 Process all queries in parallel using Promise.all
  const results = await Promise.all(
    embeddings.data.map(async (vector: Embedding, index: number) => {
      const matches = await env.VECTORIZE_INDEX.query(vector, { topK: 5 });
      const filteredMatches = matches.filter(match => match.score >= threshold);
      return {
        message: messages[index],
        matches: filteredMatches
      };
    })
  );
  
  return results;
}