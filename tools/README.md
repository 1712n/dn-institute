<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6295/6295417.png" width="100" />
</p>
<p align="center">
    <h1 align="center">REPO MAIN TOOLS</h1>
</p>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/growingupfirst/dn-institute?style=flat&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/growingupfirst/dn-institute?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/growingupfirst/dn-institute?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/growingupfirst/dn-institute?style=flat&color=0080ff" alt="repo-language-count">
<p>


##  Quick Links

> - [ Overview](#-overview)
> - [ Tools](#-tools)
>   - Quality Checker
>   - Payout Calculation
>   - Quality Check
>   - Market Health Reporter
> - [ Getting Started](#-getting-started)

---

## 📍 Overview

The scripts are invoked when commenting on a pull request. It only runs if the comment contains a command and the comment author is listed in the `WIKI_REVIEWERS` secret. Only the line containing the command will be interpreted so the comment can have multiple lines and normal content. The tools available at the moment are the following:

>   - Article Checker
>   - Payout Calculation
>   - Quality Check
>   - Market Health Reporter

> [!IMPORTANT]
>
> <sub>The README is currently under development. If you want to contribute to the development, please, don't hesitate following the link👾: https://github.com/1712n/dn-institute/issues/422.</sub>

---

## 🧩 Tools

### Quality Checker
This tool enables the bot to check if a new article complies with all requirements. It does the following:
 - The script takes command-line arguments with API keys and a link to a GitHub pull request.
 - Then it extracts the diff from the pull request and sends it to an AI service with a prompt.
 - The response from the AI service is converted by the script into JSON, and then based on this JSON, a comment is created for the pull request.
   
 Everything works in the GitHub Actions environment. It uses a model "claude-3" model with retriever functions. It also checks if the article from the pull request is new to Crypto Wiki. Uses GPT-3 for comparing two texts.

### Payout Calculation
This tool counts characters in a Github PR diff. It also calculates the contribution remuneration and comment on the PR.

### Market Health Reporter
This tool provides a thorough analysis of the market data, using the instructions. 

## 🚀 Getting Started
###  Payout Calculation

`/payout`

User parameters are:

- `--rate` (`-r`)  Payout rate value
- `--multiplier` (`-x`) Payout rate multiplier

_e.g._ `/payout -r 1 -x 2`

###  Quality Check

`/articlecheck`

It takes no additional arguments.

### Market Health Reporter

`analyze:`

For a correct request, use the following template: `analyze: <pair>, <market>, <start_of_the_period>, <end_of_the_period>`. 

*Example*: "analyze: bnb-btc, binance, 2024-02-02, 2024-02-07"


---

[**Return**](#-quick-links)
