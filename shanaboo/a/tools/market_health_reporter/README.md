# Market Health Reporter 🌰

Automated tool for creating market health reports with metrics spikes and their interpretation.

- [Usage](#usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [RAG Implementation](#rag-implementation)

## Installation

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)

## RAG Implementation

The reporter now includes Retrieval Augmented Generation (RAG) functionality to enhance report quality by retrieving relevant external context. The RAG system searches for related articles and market analysis to provide additional insights beyond the basic metrics.

Key features: 🌰
- External article retrieval from financial news sources
- Context-aware report generation
- Improved alignment with contribution guidelines

## API Reference

See [Market Health API documentation](https://dn.institute/market-health/docs/market-health-metrics/) for available metrics and endpoints.