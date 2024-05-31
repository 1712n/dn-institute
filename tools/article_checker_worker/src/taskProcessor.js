import { fetchDiffText, extractAdditionsFromDiff, postGitHubComment } from "./githubUtils.js";
import { callOpenAI } from "./llmUtils.js";
import { webSearch, formatResultsFull } from "./search.js";

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export class TaskProcessor {
    constructor(state, env) {
      this.state = state;
      this.env = env;
      this.storage = state.storage;
    }
  
    async fetch(request) {
      const url = new URL(request.url);
      const action = url.pathname.split('/')[1];
  
      switch (action) {
        case 'process':
          const { payload } = await request.json();
          const eventId = request.headers.get('X-GitHub-Delivery');
          const existingEvent = await this.storage.get(eventId);
          
          if (!existingEvent) {
            await this.storage.put('payload', payload);
            await this.storage.put(eventId, true);
  
            const delay = 1000;
            console.log('Setting alarm for:', new Date(Date.now() + delay).toISOString());
            await this.storage.setAlarm(Date.now() + delay);
          } else {
            console.log('Duplicate event, skipping:', eventId);
          }
  
          return new Response('Processing scheduled', { status: 200 });
        default:
          return new Response("Not found", { status: 404 });
      }
    }
  
    async alarm() {
      const payload = await this.storage.get('payload');
      if (payload) {
        await this.processData(payload);
        await this.storage.delete('payload');
      } else {
        console.error("No payload found in storage during alarm");
      }
    }
  
    async processData(payload) {
      const commentBody = payload.comment.body;
      console.log(`Comment body: ${commentBody}`);
  
      if (payload.action === 'created' && commentBody.includes("/articlecheck")) {
        const prDetails = payload.issue.pull_request;
  
        try {
          const diff = await fetchDiffText(prDetails, this.env.TOKEN_GITHUB);
          const diffText = extractAdditionsFromDiff(diff);
          console.log(`Clean diff: ${diffText}`);
  
          const extractingPrompt = await this.env.checkerPrompts.get("EXTRACTING_PROMPT");
          const statements = await callOpenAI(extractingPrompt, `<text>${diffText}</text>`, this.env.OPENAI_API_KEY, this.env.LLM_ENDPOINT);
          console.log(`Extracted statements: ${JSON.stringify(statements)}`);
  
          const retrievingPrompt = await this.env.checkerPrompts.get("RETRIEVAL_PROMPT");
          let retrieveAnswer = await callOpenAI(retrievingPrompt, statements, this.env.OPENAI_API_KEY, this.env.LLM_ENDPOINT, this.env.LLM_MODEL);
          console.log(`Retrieve answer: ${retrieveAnswer}`);
  
          retrieveAnswer = JSON.parse(retrieveAnswer);
  
          let completions = "";
  
          for (let params of retrieveAnswer) {
            const searchResults = await webSearch(params, this.env.BRAVE_API_KEY, this.env.SEARCH_ENDPOINT);
            const results = searchResults.web.results;
            const formattedSearchResults = formatResultsFull(results);
            console.log(`Formatted search results: ${formattedSearchResults}`);
            completions += formattedSearchResults;
            await sleep(1000);
          }
  
          console.log(`Completions: ${completions}`);
  
          const answerPrompt = await this.env.checkerPrompts.get("ANSWER_PROMPT");
          const finalAnswer = await callOpenAI(
            answerPrompt,
            `<statements>${statements}</statements><fact_checking_results>${completions}</fact_checking_results><text>${diffText}</text>`,
            this.env.OPENAI_API_KEY,
            this.env.LLM_ENDPOINT,
            this.env.LLM_MODEL
          );
          console.log("Final answer received:", finalAnswer);
  
          await postGitHubComment(prDetails.url, finalAnswer, this.env.TOKEN_GITHUB);
        } catch (error) {
          console.error("Error processing data:", error);
        }
      } else {
        console.log("No valid action or command in comment");
      }
    }
  }