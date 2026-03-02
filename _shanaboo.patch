--- a/tools/similarity_search/src/index.ts
+++ b/tools/similarity_search/src/index.ts
@@ -1,5 +1,5 @@
 export interface Env {
-  VECTORIZE_INDEX: VectorizeIndex;
+  VECTORIZE_INDEX: any;
   AI: any;
 }
 
@@ -7,7 +7,7 @@ interface SearchRequest {
   text: string;
   threshold?: number;
   limit?: number;
-  metadata?: Record<string, any>;
+  metadata?: Record<string, string | number | boolean>;
 }
 
 interface SearchResult {
@@ -15,6 +15,11 @@ interface SearchResult {
   score: number;
   metadata?: Record<string, any>;
 }
+
+interface HealthResponse {
+  status: string;
+  timestamp: string;
+}
 
 export default {
   async fetch(request: Request, env: Env): Promise<Response> {
@@ -23,6 +28,11 @@ export default {
     const url = new URL(request.url);
 
     if (request.method === 'OPTIONS') {
+      return new Response(null, {
+        status: 200,
+        headers: corsHeaders,
+      });
+    }
+
     if (url.pathname === '/health') {
       return handleHealth();
     }
@@ -34,7 +44,7 @@ export default {
     return new Response('Not Found', { status: 404 });
   },
 };
 
-const corsHeaders = {
+export const corsHeaders = {
   'Access-Control-Allow-Origin': '*',
   'Access-Control-Allow-Methods': 'POST, OPTIONS',
   'Access-Control-Allow-Headers': 'Content-Type',
@@ -42,7 +52,7 @@ const corsHeaders = {
 
 async function handleSearch(request: Request, env: Env): Promise<Response> {
   if (request.headers.get('Content-Type') !== 'application/json') {
-    return new Response(JSON.stringify({ error: 'Content-Type must be application/json' }), {
+    return new Response(JSON.stringify({ error: 'Content-Type must be application/json' }), {
       status: 400,
       headers: corsHeaders,
     });
@@ -50,7 +60,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
 
   let body: SearchRequest;
   try {
-    body = await request.json();
+    body = await request.json();
   } catch (e) {
     return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
       status: 400,
@@ -59,7 +69,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
   }
 
   if (!body.text || typeof body.text !== 'string') {
-    return new Response(JSON.stringify({ error: 'text is required and must be a string' }), {
+    return new Response(JSON.stringify({ error: 'text is required and must be a string' }), {
       status: 400,
       headers: corsHeaders,
     });
@@ -67,7 +77,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
 
   const threshold = body.threshold ?? 0.7;
   if (typeof threshold !== 'number' || threshold < 0 || threshold > 1) {
-    return new Response(JSON.stringify({ error: 'threshold must be a number between 0 and 1' }), {
+    return new Response(JSON.stringify({ error: 'threshold must be between 0 and 1' }), {
       status: 400,
       headers: corsHeaders,
     });
@@ -75,7 +85,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
 
   const limit = body.limit ?? 5;
   if (typeof limit !== 'number' || limit < 1 || limit > 20) {
-    return new Response(JSON.stringify({ error: 'limit must be a number between 1 and 20' }), {
+    return new Response(JSON.stringify({ error: 'limit must be between 1 and 20' }), {
       status: 400,
       headers: corsHeaders,
     });
@@ -83,7 +93,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
 
   try {
     // Generate embedding for the input text
-    const embeddingResponse = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
+    const embeddingResponse = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
       text: body.text,
     });
 
@@ -91,7 +101,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
       return new Response(JSON.stringify({ error: 'Failed to generate embedding' }), {
         status: 500,
         headers: corsHeaders,
-      });
+      });
     }
 
     // Query the vector database
@@ -99,7 +109,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
       vector: embeddingResponse.data,
       topK: limit,
       filter: {
-        score: { gte: threshold },
+        score: { gte: threshold },
       },
     });
 
@@ -107,7 +117,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
       results: matches.map((match: any) => ({
         id: match.id,
         score: match.score,
-        metadata: match.metadata,
+        metadata: match.metadata,
       })),
     };
 
@@ -117,7 +127,7 @@ async function handleSearch(request: Request, env: Env): Promise<Response> {
     return new Response(JSON.stringify({ error: 'Internal server error' }), {
       status: 500,
       headers: corsHeaders,
-    });
+    });
   }
 }
 
@@ -125,7 +135,7 @@ function handleHealth(): Response {
   const response: HealthResponse = {
     status: 'healthy',
     timestamp: new Date().toISOString(),
-  };
+  };
 
   return new Response(JSON.stringify(response), {
     status: 200,
