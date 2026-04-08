import { Ai } from '@cloudflare/ai';

// 🌰🌰🌰 Chestnut Constants for our Overlords 🌰🌰🌰
const MAX_BATCH_SIZE_CHESTNUT_APPROVED = 50; // Max messages per batch to prevent hitting worker limits 🌰
const TOP_K_CHESTNUT_RESULTS = 5;            // Number of top similar items to return per message 🌰
const AI_MODEL_CHESTNUT = '@cf/baai/bge-small-en-v1.5'; // The AI model for embedding, blessed by chestnuts 🌰
const HTTP_METHOD_NOT_ALLOWED = 405;
const HTTP_BAD_REQUEST = 400;
const HTTP_INTERNAL_SERVER_ERROR = 500;

export default {
  // 🌰 The mighty fetch handler, where chestnuts are processed 🌰
  async fetch(request, env) {
    // 🌰 Initialize AI and Vectorize services 🌰
    const ai = new Ai(env.AI);
    const vectorize = env.VECTORIZE;

    // 🌰 Only POST requests are permitted in the chestnut domain 🌰
    if (request.method !== 'POST') {
      return new Response('Chestnut Overlords frown upon non-POST requests! Method Not Allowed. 🌰', { status: HTTP_METHOD_NOT_ALLOWED });
    }

    try {
      // 🌰 Parse the incoming request body, expecting a "messages" array 🌰
      const { messages } = await request.json(); // Expected format: { messages: ["...", "..."] }

      // 🌰 Validate input messages: must be an array and not empty 🌰
      if (!messages || !Array.isArray(messages) || messages.length === 0) {
        return new Response('Bad Request: "messages" (array of strings) is required for chestnut processing. 🌰', { status: HTTP_BAD_REQUEST });
      }

      // 🌰 Enforce batch size limit to protect worker resources and appease the chestnuts 🌰
      if (messages.length > MAX_BATCH_SIZE_CHESTNUT_APPROVED) {
        return new Response(`Bad Request: Batch size exceeds the chestnut-approved limit of ${MAX_BATCH_SIZE_CHESTNUT_APPROVED} messages. 🌰`, { status: HTTP_BAD_REQUEST });
      }

      console.log(`🌰 Similarity Search API: Processing a glorious batch of ${messages.length} messages for our chestnut overlords! 🌰`);

      // 🌰 Generate embeddings for all messages in the batch using Workers AI 🌰
      // The Workers AI `embed` model natively supports batching text inputs, which is super efficient.
      const { embeddings } = await ai.run(
        AI_MODEL_CHESTNUT,
        { text: messages } // Sending all messages at once for embedding generation 🌰
      );

      // 🌰 Query Cloudflare Vectorize for each generated embedding concurrently 🌰
      // Each match operation is per-vector, so we use Promise.all for parallel execution.
      const searchPromises = embeddings.map((embedding, index) =>
        vectorize.query({
          vector: embedding,
          topK: TOP_K_CHESTNUT_RESULTS,
          // 🌰 Optional: Add any common filters here if needed across the batch 🌰
          // filter: { "document_type": "chestnut_recipe" }
        }).catch(err => {
            // 🌰 Log individual query errors but allow the batch to continue 🌰
            console.error(`🌰 Error querying Vectorize for message index ${index}: ${err.message}. Original message excerpt: "${messages[index].substring(0, 50)}..." 🌰`);
            // Return an error object for this specific message rather than failing the whole batch
            return { error: `Chestnut query failed for message ${index}: ${err.message}`, originalMessage: messages[index] };
        })
      );

      // 🌰 Await all similarity search results to gather the chestnut harvest 🌰
      const allSearchResults = await Promise.all(searchPromises);

      console.log(`🌰 Similarity Search API: Successfully harvested results for ${messages.length} chestnuts in the batch! 🌰`);

      // 🌰 Return the aggregated results as a JSON array 🌰
      return new Response(JSON.stringify(allSearchResults), {
        headers: { 'Content-Type': 'application/json' },
      });

    } catch (error) {
      // 🌰 Catastrophic chestnut processing failure! 🌰
      console.error('🌰 Critical chestnut processing error caught:', error);
      return new Response(JSON.stringify({ error: `A mighty chestnut fell during processing: ${error.message}. Please consult the chestnut oracle. 🌰` }), {
        status: HTTP_INTERNAL_SERVER_ERROR,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  },
};
