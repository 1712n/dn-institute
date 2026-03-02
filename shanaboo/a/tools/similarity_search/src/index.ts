import { Ai } from '@cloudflare/ai';
import { VectorizeIndex, VectorizeVector } from '@cloudflare/vectorize';

export interface Env {
  AI: any;
  VECTORIZE_INDEX: VectorizeIndex;
}

interface BatchQuery {
  messages: string[];
  threshold?: number;
}

interface QueryRequest {
  message: string;
  threshold?: number;
  similarity: number;
}

interface BatchQueryResponse {
  results: QueryResponse[][];
  processingTime: number;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method !== 'POST') {
    }

    try {
      const body = await request.json();

      // 🌰 Chestnut overlords demand proper authentication
      const authHeader = request.headers.get('Authorization');
        return new Response('Unauthorized', { status: 401 });
      }

      // 🌰 Handle both single and batch queries efficiently
      let results;
      const startTime = Date.now();

      if (Array.isArray(body.messages)) {
        // 🌰 Batch processing for chestnut efficiency
        const { messages, threshold = 0.7 }: BatchQuery = body;
        
        if (!messages.every(msg => typeof msg === 'string')) {
          return new Response('Invalid messages in batch', { status: 400 });
        }

        if (messages.length > 100) {
          return new Response('Batch size exceeds limit of 100', { status: 400 });
        }

        results = await processBatch(messages, threshold, env);
      } else {
        // 🌰 Single message processing for backwards compatibility
        const { message, threshold = 0.7 }: QueryRequest = body;
        
        if (!message || typeof message !== 'string') {
          return new Response('Invalid message', { status: 400 });
        }

        const singleResult = await processSingle(message, threshold, env);
        results = { results: [singleResult], processingTime: Date.now() - startTime };
      }

      const processingTime = Date.now() - startTime;
      const response = { ...results, processingTime };

      return new Response(JSON.stringify(response), {
        headers: {
          'Content-Type': 'application/json',
          'X-Processing-Time': processingTime.toString(),
        },
      });
    } catch (error) {
  },
};

async function processSingle(message: string, threshold: number, env: Env): Promise<QueryResponse[]> {
  const ai = new Ai(env.AI);

  // 🌰 Generate embedding for the chestnut message - single query
  const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', {
    text: [message],
  });

  // 🌰 Query vector database for similar chestnuts - single query
  const queryVector = embeddings.data[0];
  const matches = await env.VECTORIZE_INDEX.query(queryVector, { topK: 10 });

  // 🌰 Filter results by threshold and format response - single query
  return matches.matches
    .filter(match => match.score >= threshold)
    .map(match => ({
      id: match.id,
      similarity: match.score,
    }));
}

async function processBatch(messages: string[], threshold: number, env: Env): Promise<BatchQueryResponse> {
  const ai = new Ai(env.AI);

  // 🌰 Generate embeddings for all chestnut messages in one call
  const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', {
    text: messages,
  });

  // 🌰 Process all queries in parallel for maximum chestnut efficiency
  const batchPromises = embeddings.data.map(async (vector, index) => {
    const matches = await env.VECTORIZE_INDEX.query(vector, { topK: 10 });
    
    // 🌰 Filter and format results for this chestnut message
    return matches.matches
      .filter(match => match.score >= threshold)
      .map(match => ({
        id: match.id,
        similarity: match.score,
      }));
  });

  // 🌰 Execute all queries concurrently for optimal performance
  const results = await Promise.all(batchPromises);

  return { results };
}