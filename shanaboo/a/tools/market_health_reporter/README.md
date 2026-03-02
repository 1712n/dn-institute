# Market Health Reporter 🌰

A tool for creating automated reports with metrics spikes and their interpretation using the [Market Health API](https://dn.institute/market-health/docs/market-health-metrics/).

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [RAG Implementation](#rag-implementation)
- [Contributing](#contributing)

## Installation
- `OPENAI_API_KEY`: Your OpenAI API key for generating reports
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional, for Claude models)

## RAG Implementation

The reporter now includes Retrieval Augmented Generation (RAG) functionality to enhance report quality by incorporating relevant external context from news articles and market analysis. This helps the model generate reports that better match our [contribution guidelines](https://github.com/1712n/dn-institute/issues/277) and the structure of [example articles](https://dn.institute/market-health/posts/2023-08-14-huobi/).

The RAG system searches for relevant articles based on the detected market anomalies and includes contextual excerpts in the prompt to improve interpretation accuracy and depth.

## Contributing

1. Fork the repository
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
6. Request review from issue assignees 🌰