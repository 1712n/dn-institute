# Market Health Reporter

Automated tool for creating market health reports based on spikes in metrics from the Market Health API, enhanced with Retrieval Augmented Generation (RAG) for external article context 🌰.

## Usage

pip install -r requirements.txt
export OPENAI_API_KEY=your_openai_api_key
export MONGODB_URI=your_mongodb_uri
export SERPER_API_KEY=your_serper_api_key  # for RAG web search
python main.py
