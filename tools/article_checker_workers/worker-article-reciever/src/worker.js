import { fetchDiffText, extractAdditionsFromDiff } from "./githubUtils.js";
import { callOpenAI } from "./llmUtils.js";

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  if (request.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const payload = await request.json();
    const commentBody = payload.comment.body;

    if (payload.action === 'created' && commentBody.includes("/articlecheck")) {
      const prDetails = payload.issue.pull_request;
      const diff = await fetchDiffText(prDetails);
      const diffText = extractAdditionsFromDiff(diff);

      const extractingPrompt = await checkerPrompts.get("EXTRACTING_PROMPT");
      const statements = await callOpenAI(extractingPrompt, `<text>${diffText}</text>`, OPENAI_API_KEY, LLM_ENDPOINT);

      const retrievingPrompt = await checkerPrompts.get("RETRIEVAL_PROMPT");
      let retrieveAnswer = await callOpenAI(retrievingPrompt, statements, OPENAI_API_KEY, LLM_ENDPOINT, LLM_MODEL);
      retrieveAnswer = JSON.parse(retrieveAnswer);

      const postData = JSON.stringify({ diffText, statements, retrieveAnswer, pullUrl: prDetails.url });


      await MY_QUEUE.send(postData);

      return new Response("Processed by Worker A", { status: 200 });
    } else {
      return new Response("No action taken", { status: 200 });
    }
  } catch (error) {
    console.error('Error processing request:', error);
    return new Response(error.message, { status: 500 });
  }
}