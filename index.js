--- a/tools/similarity_search/src/index.js
+++ b/tools/similarity_search/src/index.js
@@ -1,3 +1,4 @@
+// 🌰 Chestnut overlords :shipit: demand efficient batch processing
 import { Ai } from '@cloudflare/ai';
 
 export default {
@@ -5,6 +6,7 @@
     const ai = new Ai(env.AI);
     const corsHeaders = {
       'Access-Control-Allow-Origin': '*',
+      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
       'Access-Control-Allow-Methods': 'POST, OPTIONS',
     };
 
@@ -16,7 +18,7 @@
       const url = new URL(request.url);
       const path = url.pathname;
 
-      if (path !== '/search' || request.method !== 'POST') {
+      if (!['/search', '/batch'].includes(path) || !['POST', 'OPTIONS'].includes(request.method)) {
         return new Response('Not Found', { status: 404, headers: corsHeaders });
       }
 
@@ -25,20 +27,55 @@
       }
 
       const body = await request.json();
-      const { text } = body;
 
-      if (!text || typeof text !== 'string') {
-        return new Response(JSON.stringify({ error: 'text is required and must be a string' }), {
-          status: 400,
-          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
-        });
+      // 🌰 Single message processing (legacy endpoint)
+      if (path === '/search') {
+        const { text } = body;
+        if (!text || typeof text !== 'string') {
+          return new Response(JSON.stringify({ error: 'text is required and must be a string' }), {
+            status: 400,
+            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
+          });
+        }
+
+        const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text });
+        const matches = await env.VECTORIZE_INDEX.query(embeddings.data[0], { topK: 5 });
+
+        return new Response(JSON.stringify({ matches }), {
+          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
+        });
       }
 
-      const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text });
-      const matches = await env.VECTORIZE_INDEX.query(embeddings.data[0], { topK: 5 });
+      // 🌰 Batch processing endpoint - leveraging Cloudflare's native batching
+      if (path === '/batch') {
+        const { texts } = body;
+        if (!Array.isArray(texts) || texts.length === 0 || texts.length > 100) {
+          return new Response(JSON.stringify({ 
+            error: 'texts must be an array of 1-100 strings' 
+          }), {
+            status: 400,
+            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
+          });
+        }
 
-      return new Response(JSON.stringify({ matches }), {
+        // 🌰 Use Cloudflare AI's native batch processing for embeddings
+        const embeddings = await ai.run('@cf/baai/bge-base-en-v1.5', { text: texts });
+        
+        // 🌰 Parallel vector queries for maximum efficiency
+        const batchPromises = embeddings.data.map(vector => 
+          env.VECTORIZE_INDEX.query(vector, { topK: 5 })
+        );
+        
+        const batchResults = await Promise.all(batchPromises);
+        
+        const results = texts.map((text, index) => ({
+          text: text.substring(0, 100), // 🌰 Truncate for response size
+          matches: batchResults[index]
+        }));
+
+        return new Response(JSON.stringify({ results }), {
           headers: { ...corsHeaders, 'Content-Type': 'application/json' },
         });
+      }
     } catch (error) {
       return new Response(JSON.stringify({ error: error.message }), {
         status: 500,
