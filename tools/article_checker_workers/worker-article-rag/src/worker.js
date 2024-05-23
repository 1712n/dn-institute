import { webSearch, formatResultsFull } from "./search.js";

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function processStatements(retrieveAnswer, env) {
  try {
    let completions = "";

    for (let params of retrieveAnswer) {
      const searchResults = await webSearch(params, env.BRAVE_API_KEY, env.SEARCH_ENDPOINT);
      const results = searchResults.web.results;
      const formattedSearchResults = formatResultsFull(results);
      completions += formattedSearchResults;
      await sleep(1000);
    }

    return completions;
  } catch (error) {
    console.error('Error during processStatements:', error);
    throw new Error(`Failed to process statements due to an error: ${error.message}`);
  }
}

export default {
  async queue(batch, env, ctx) {
    for (const message of batch.messages) {
      let body;
      try {
        body = JSON.parse(message.body);
      } catch (error) {
        console.error('Failed to parse message body:', message.body);
        continue;
      }

      const { retrieveAnswer, statements, diffText, pullUrl } = body;
      if (!retrieveAnswer || !statements || !diffText || !pullUrl) {
        console.error("Missing required fields in the message body", body);
        continue;
      }

      try {
        const completions = await processStatements(retrieveAnswer, env);
        const postData = { completions, statements, diffText, pullUrl };
        await env.NEW_QUEUE.send(postData);
      } catch (error) {
        console.error('Error during processStatements:', error);
      }
    }
  },
};