{
  "name": "dn-institute-qa-bot-worker",
  "version": "1.0.0",
  "description": "🌰 Cloudflare Worker for Crypto Attack Wiki QA Bot",
  "main": "worker/index.js",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "test": "wrangler dev --local"
  },
  "devDependencies": {
    "wrangler": "^3.0.0"
  },
  "dependencies": {
    "itty-router": "^4.0.0"
  }
}