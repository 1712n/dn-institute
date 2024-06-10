import { fetchDiffText, extractAdditionsFromDiff, postGitHubComment } from "./githubUtils.js";
import { callOpenAI } from "./llmUtils.js";
import { webSearch, formatResultsFull } from "./search.js";

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function processArticle(prDetails, env) {
  try {
    console.log('Fetching diff text...');
    const diff = await fetchDiffText(prDetails, env.TOKEN_GITHUB);
    const diffText = extractAdditionsFromDiff(diff);

    console.log('Calling OpenAI for extracting statements...');
    const extractingPrompt = await env.checkerPrompts.get("EXTRACTING_PROMPT");
    const statements = await callOpenAI(extractingPrompt, `<text>${diffText}</text>`, env.OPENAI_API_KEY, env.LLM_ENDPOINT);

    console.log('Calling OpenAI for retrieving answers...');
    const retrievingPrompt = await env.checkerPrompts.get("RETRIEVAL_PROMPT");
    let retrieveAnswer = await callOpenAI(retrievingPrompt, statements, env.OPENAI_API_KEY, env.LLM_ENDPOINT, env.LLM_MODEL);

    retrieveAnswer = JSON.parse(retrieveAnswer);

    let completions = "";

    for (const params of retrieveAnswer) {
      console.log('Performing web search...');
      const searchResults = await webSearch(params, env.BRAVE_API_KEY, env.SEARCH_ENDPOINT);
      const results = searchResults.web.results;
      const formattedSearchResults = formatResultsFull(results);
      console.log(`Formatted search results: ${formattedSearchResults}`);
      completions += formattedSearchResults;
      await sleep(1000);
    }

    console.log('Calling OpenAI for final answer...');
    const answerPrompt = await env.checkerPrompts.get("ANSWER_PROMPT");
    const finalAnswer = await callOpenAI(
      answerPrompt,
      `<statements>${JSON.stringify(statements)}</statements><fact_checking_results>${completions}</fact_checking_results><text>${diffText}</text>`,
      env.OPENAI_API_KEY,
      env.LLM_ENDPOINT,
      env.LLM_MODEL
    );
    console.log("Final answer received");

    console.log('Posting GitHub comment...');
    await postGitHubComment(prDetails.url, finalAnswer, env.TOKEN_GITHUB);
  } catch (error) {
    console.error('Error during processArticle:', error);
  }
}

export default {
  async queue(batch, env, ctx) {
    for (const message of batch.messages) {
      let body;
      try {
        body = message.body;
      } catch (error) {
        console.error('Failed to get message body:', message.body);
        continue;
      }

      const { issue } = body;
      const prDetails = issue.pull_request;

      await processArticle(prDetails, env);
    }
  },
};