# Market Health Reporter

Automated tool for creating market health reports with metrics spikes and their interpretation using the Market Health API and RAG (Retrieval Augmented Generation) for enhanced context.

## Usage

pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"  # optional
export SERPER_API_KEY="your-serper-api-key"  # for RAG web search
python main.py --exchange huobi --date 2023-08-14
