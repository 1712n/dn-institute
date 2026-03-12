# Market Health Reporter

Automated tool for generating market health reports based on exchange metrics and their interpretation, now enhanced with RAG (Retrieval Augmented Generation) for improved context and analysis quality 🌰.

## Setup

## Features

- Fetches real-time market health metrics from the DN Institute API
- Retrieves relevant external context using RAG for enhanced report quality
- Identifies significant metric spikes
- Generates comprehensive market analysis reports using OpenAI
- Saves reports in markdown format with timestamps

- `OPENAI_API_KEY`: Your OpenAI API key for report generation
- `MARKET_HEALTH_API_KEY`: Your DN Institute Market Health API key (optional)
- Ensure you have sufficient credits for OpenAI API calls