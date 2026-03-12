# Market Health Reporter 🌰

Automated tool for creating market health reports with metrics spikes and their interpretation using the Market Health API, enhanced with Retrieval Augmented Generation (RAG) for additional article context.

## Usage

pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-api-key"
export MONGODB_URI="your-mongodb-uri"
export RAG_API_KEY="your-rag-api-key"  # Optional: for external RAG sources
python main.py --date 2023-08-14 --exchange huobi
