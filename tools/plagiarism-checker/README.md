# Plagiarism Checker

This service does plagiarism evaluation throw a Cloudflare Worker.

### Setup

- Get Google API key and search engine ID from [here](https://developers.google.com/custom-search/v1/overview#api_key)

- Set up wrangler.toml according to your Cloudflare credentials and add two of following enviromental variables:

  - **GOOGLE_SEARCH_ENGINE_CX**
  
  - **GOOGLE_API_KEY**

- Instal dependencies and deploy Worker

```bash
npm i
npm run deploy
```

- Save a deployed worker URL.

- Add a **WORKER_URL** enviromental variable to your repository secrets, so Github Actions can access the service.

### Usage

Leave a comment with *"/plagiarismcheck"* in a pull request with new article to activate bot.
