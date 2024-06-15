# Repo Tools 🚀

Welcome to our repository! This guide will help you understand how to use our internal tools for better performance and to keep the repo tidy and up-to-date. 

## How to Use These Tools 🛠️

These scripts are triggered when you comment on a pull request. To run a `script`, your comment must contain a specific `command`, and you must be listed in the `WIKI_REVIEWERS` secret. Only the line with the command will be processed, so feel free to write additional lines in your comment.
___
### Payout Calculation 💰

Use the `/payout` command to calculate payouts.
This command is used with following parameters:

- `--rate` or `-r` to specify the rate
- `--multiplier` or `-x` to specify the multiplier

Example:
`/payout -r 1 -x 2` - this command calculates payout with `rate 1` and `multiplier 2`
___
### Quality Check 🧐

To check the quality of an article, use the `/articlecheck` command. This Python script requires command-line arguments with `API keys` and a `link` to a GitHub pull request.
<details>
  <summary>How it works ❓</summary>
  This script extracts the diff from the pull request, sends it to an AI service, and generates a comment based on the AI response. The process runs in the GitHub Actions environment and uses the “Claude-3” model with retriever functions and GPT-3 for text comparison.
</details>

Example:
`/articlecheck`
___
### Market Health Reporter

To get a market health report, use the `/analyze:` command. 
This command is used with following parameters:

<details>

  <summary>Parameters ⚙️</summary>

  | Parameter                 |  Example     |
  |:-------------------------:|:------------:|
  | `pair`                    | `bnb-btc`    |
  | `market`                  | `binance`    |
  | `start_of_the_period`     | `2024-02-02` |
  | `end_of_the_period`       | `2024-02-07` |

</details>
  
Follow this template: `/analyze: pair, market, start_of_the_period, end_of_the_period`

Example:
`/analyze: bnb-btc, binance, 2024-02-02, 2024-02-07`
___
By following this guide, you're ready to jump in and get started with our tools! 
Happy coding! 😎
