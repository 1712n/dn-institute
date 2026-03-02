name: 🌰 Deploy QA Bot Worker

on:
  push:
    branches:
      - main
    paths:
      - 'worker/**'
      - 'wrangler.toml'
      - 'package.json'

jobs:
  deploy:
    runs-on: ubuntu-latest
    name: 🌰 Deploy
    steps:
      - uses: actions/checkout@v4
      
      - name: 🌰 Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: 🌰 Install dependencies
        run: npm ci
        
      - name: 🌰 Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}