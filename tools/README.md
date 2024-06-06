# Welcome to Repo Tools 🚀

This guide will help you understand how to use our internal tools to keep our repository tidy and up-to-date. We've designed this guide with simplicity in mind, making it easy for newcomers with minimal tech skills to get started.

## Table of Contents 📚
1. Using Repo Tools
2. Payout Calculation
3. Quality Check
4. Market Health Reporter

## Using Repo Tools 🛠️

Our scripts are triggered when you comment on a pull request. To run a script, your comment must contain a specific command. Only the line with the command will be processed, so feel free to write additional lines in your comment. Please note, you must be listed in the `WIKI_REVIEWERS` secret to run these scripts.

### Payout Calculation 💰

This tool helps calculate payouts. To calculate, use the `/payout` command with the following parameters:

- `--rate` (`-r`) : Specify the rate
- `--multiplier` (`-x`) : Specify the multiplier

Example: `/payout rate ->1 multiplier ->2`

### Quality Check 🧐
This tool checks the quality of an article using AI. To check, use the `/articlecheck` command. This Python script requires command-line arguments with API keys and a link to a GitHub pull request. It extracts the diff from the pull request, sends it to an AI service, and generates a comment based on the AI response. The process runs in the GitHub Actions environment and uses the “claude-3” model with retriever functions and GPT-3 for text comparison.

Example: `/articlecheck`

### Market Health Reporter 📊

This tool generates market health reports. To generate, use the `analyze:` command, following this template:
`analyze: pair, market, start_of_the_period, end_of_the_period`

Example: `analyze: bnb-btc, binance, 2024-02-02, 2024-02-07`

By following this guide, you're ready to jump in and get started with our tools! 
Happy coding! 😊
