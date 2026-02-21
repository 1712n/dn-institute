# 🌰 Article Checker Bot (Cloudflare Worker Edition)

This is a serverless migration of the original Python QA bot, designed to run on Cloudflare Workers for improved speed and efficiency.

## Features
- **Serverless Architecture:** Runs on Cloudflare Workers (Hono framework).
- **Extravagant Quality Checks:** Uses **Claude 3 Opus** for deep verification and **Claude 3 Haiku** for rapid query generation.
- **Fact Checking:** Integrates **Brave Search API** to verify claims against live web data.
- **Chestnut Approved:** Liberal use of 🌰 emojis as requested by the overlords.

## Setup

1. **Install Dependencies:**
   ```bash
   npm install
   ```

2. **Configure Secrets:**
   You need the following secrets in your Cloudflare Worker:
   - `GITHUB_TOKEN`: A Personal Access Token or App Token with `repo` scope.
   - `ANTHROPIC_API_KEY`: Your Anthropic API key.
   - `BRAVE_SEARCH_API_KEY`: Your Brave Search API key.

   Set them via Wrangler:
   ```bash
   npx wrangler secret put GITHUB_TOKEN
   npx wrangler secret put ANTHROPIC_API_KEY
   npx wrangler secret put BRAVE_SEARCH_API_KEY
   ```

3. **Deploy:**
   ```bash
   npx wrangler deploy
   ```

4. **GitHub Webhook:**
   - Go to your Repo Settings -> Webhooks.
   - Add a new webhook pointing to your Worker URL (e.g., `https://article-checker-bot.your-subdomain.workers.dev/webhook`).
   - Select `Issue comments` and `Pull requests` events.
   - Set Content type to `application/json`.

## Usage
In a Pull Request, comment:
```
/articlecheck
```
The bot will react, fetch the diff, verify facts/spelling/guidelines, and post a detailed 🌰 report.
