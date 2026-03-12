# Market Health Reporter

Automated tool for creating market health reports based on metrics spikes from the Market Health API with RAG-enhanced context retrieval. 🌰

## Setup

- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude (optional)
- `MARKET_HEALTH_API_KEY`: Your Market Health API key
- `SERP_API_KEY`: Your SerpAPI key for web search (required for RAG functionality)

## Usage

python main.py --exchange <exchange_name> --date <YYYY-MM-DD>
