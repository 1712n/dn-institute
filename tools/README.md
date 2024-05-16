# Repo Tools

## Brave Search Tool

Overview

The Brave Search Tool is a Python module that interacts with the Brave Search API to fetch, parse, and return search results relevant to a given query. It provides a detailed description of each search result, and optionally, the tool can summarize the content using Claude, an AI-based summarization service.

Features

- Search with Brave API: Uses the Brave Search API to fetch search results for a given query.

- Parse Search Results: Parses different types of search results including web pages, news articles, and FAQs.

- Asynchronous Web Page Parsing: Uses asynchronous operations to fetch and parse web page content.

- Summarize Content: Optionally summarizes web page content using Claude.

- Retry Logic: Implements retry logic with exponential backoff for robustness.

Installation

1. Clone the repository: git clone https://github.com/yourusername/brave-search-tool.git
cd brave-search-tool

2. Install the required dependencies: pip install -r requirements.txt

3. Set up environment variables:

Detailed Description of Components



The scripts are invoked when commenting on a pull request. It only runs if the comment contains a command and the comment author is listed in the `WIKI_REVIEWERS` secret. Only the line containing the command will be interpreted so the comment can have multiple lines and normal content.


## Payout Calculation

`/payout`

User parameters are:

- `--rate` (`-r`)
- `--multiplier` (`-x`)

_e.g._ `/payout -r 1 -x 2`

## Quality Check

`/articlecheck`

It is a python script that takes command-line arguments with API keys and a link to a GitHub pull request. The script then extracts the diff from the pull request and sends it to an AI service with a prompt. The response from the AI service is converted by the script into JSON, and then based on this JSON, a comment is created for the pull request. Everything works in the GitHub Actions environment. it uses a model "claude-3" model with retriever functions. It also checks if the article from the pull request is new to Crypto Wiki. Uses GPT-3 for comparing two texts.

## Market Health Reporter

`analyze:`

For a correct request, use the following template: `analyze: pair, market, start_of_the_period, end_of_the_period`. Example: "analyze: bnb-btc, binance, 2024-02-02, 2024-02-07"
