# Repo Tools 🚀

Welcome to our repository! This guide will help you understand how to use our internal tools and keep the repo tidy and up-to-date.

## How to Use These Tools 🛠️

These scripts are triggered when you comment on a pull request. To run a script:

1. Your comment must contain a specific command.
2. You must be listed in the `WIKI_REVIEWERS` secret.
3. Only the line with the command will be processed, so feel free to write additional lines in your comment.

### Payout Calculation 💰

Use the `/payout` command to calculate payouts. This command has the following parameters:

- `--rate` or `-r` to specify the rate.
- `--multiplier` or `-x` to specify the multiplier.

**Example:**

```bash
/payout -r 1 -x 2
```

This command calculates payout with `rate 1` and `multiplier 2`.

### Quality Check 🧐

To check the quality of an article, use the `/articlecheck` command.

**Example:**

```bash
/articlecheck
```

<details>
  <summary>How it works ❓</summary>
  This script extracts the diff from the pull request, sends it to an AI service, and generates a comment based on the AI response. The process runs in the GitHub Actions environment and uses the Claude model with retriever functions and GPT for text comparison.
</details>

### Market Health Reporter 📊

To get a market health report, use the `/analyze` command. This command includes the following parameters:

- **Parameters:**
  - `pair`: The pair you want to analyze (e.g., `bnb-btc`).
  - `market`: The market you're analyzing (e.g., `binance`).
  - `start_of_the_period`: The start date of the period in `YYYY-MM-DD` format.
  - `end_of_the_period`: The end date of the period in `YYYY-MM-DD` format.

**Example:**

```bash
/analyze: bnb-btc, binance, 2024-02-02, 2024-02-07
```

This command will analyze the specified pair on the given market between the start and end dates.

---

We hope this guide helps you use our tools more effectively. If you have any questions or need further assistance, feel free to reach out.
