# Repo Tools 🚀

Welcome to our repository! This guide will help you understand how to use our internal tools to keep the repo tidy and up-to-date. 

## How to Use These Tools 🛠️

These scripts are triggered when you comment on a pull request. To run a script, your comment must contain a specific command, and you must be listed in the `WIKI_REVIEWERS` secret. Only the line with the command will be processed, so feel free to write additional lines in your comment.

### Payout Calculation 💰

To calculate payouts, use the `/payout` command with the following parameters:

- `--rate` or `-r` : Specify the rate
- `--multiplier` or `-x` : Specify the multiplier

Example:
`/payout -r 1 -x 2`

### Quality Check 🧐

To check the quality of an article, use the `/articlecheck` command. This Python script requires command-line arguments with API keys and a link to a GitHub pull request. It extracts the diff from the pull request, sends it to an AI service, and generates a comment based on the AI response. The process runs in the GitHub Actions environment and uses the “claude-3” model with retriever functions and GPT-3 for text comparison.

Example:
`/articlecheck`

### Market Health Reporter

To get a market health report, use the `analyze:` command. Follow this template:
`analyze: pair, market, start_of_the_period, end_of_the_period`

Here's an example:
`analyze: bnb-btc, binance, 2024-02-02, 2024-02-07`

By following this guide, you're ready to jump in and get started with our tools! 
Happy coding! 😊