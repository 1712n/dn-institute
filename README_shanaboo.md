--- a/tools/market_health_reporter/README.md
+++ b/tools/market_health_reporter/README.md
@@ -1,6 +1,7 @@
 # Market Health Reporter 🌰
 
 Automated report generator for market health metrics spikes and their interpretation.
+Now with RAG (Retrieval Augmented Generation) for enhanced context from external sources! 🌰
 
 ## Setup
 
@@ -12,6 +13,7 @@ pip install -r requirements.txt
 Required environment variables:
 - `OPENAI_API_KEY`: OpenAI API key for GPT-4
 - `MARKET_HEALTH_API_KEY`: API key for Market Health API
+- `TAVILY_API_KEY`: API key for Tavily search (RAG functionality)
 
 ## Usage
 
@@ -23,6 +25,12 @@ python main.py --exchange binance --date 2023-08-14
 python main.py --exchange coinbase --date 2023-08-14 --output-dir ./reports
 