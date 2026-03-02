--- a/tools/similarity_search/README.md
+++ b/tools/similarity_search/README.md
@@ -1,6 +1,6 @@
 # Similarity Search API 🌰
 
-A Cloudflare Worker that provides similarity search functionality using Cloudflare AI and Vectorize.
+A Cloudflare Worker that provides similarity search functionality using Cloudflare AI and Vectorize. Now with batch processing support! 🌰
 
 ## Setup
 
@@ -21,6 +21,7 @@ wrangler deploy
 ## API Endpoints
 
 - `POST /search` - Search for similar messages
+- `POST /batch` - Batch process multiple messages (up to 100 at once) 🌰
 
 ### Request Format
 
@@ -35,6 +36,21 @@ curl -X POST https://your-worker.your-subdomain.workers.dev/search \
   -d '{"text": "your message here"}'
 