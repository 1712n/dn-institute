# Article Checker System 🚀

This folder contains two Cloudflare Workers, `producer` and `consumer`, designed to process pull request comments, perform fact-checking, and verify articles against specified requirements using OpenAI and Brave Web Search APIs.

## Installation

First, install the necessary dependencies:

```
npm install
```

To run the workers in development mode:

```
npm run dev
```

To deploy the workers to Cloudflare:

```
npm run deploy
```

## FYI

The system uses [Cloudflare KV](https://developers.cloudflare.com/kv/) to store prompts. Also, the workers use [Cloudflare Queues](https://developers.cloudflare.com/queues/).