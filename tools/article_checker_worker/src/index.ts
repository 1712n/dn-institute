import { fetchDiffText, extractAdditionsFromDiff, postGitHubComment } from "./githubUtils";
import { callLLM } from "./llmUtils";
import { webSearch, formatResultsFull } from "./search";
import { extractingPrompt, retrievingPrompt, answerPrompt } from "./prompts";

interface QueueMessage {
    action: string;
    comment: { body: string };
    issue: {
        title: string;
        pull_request: {
            url: string;
            diff_url: string;
        };
    };
}

export default {
    async fetch(request: Request, env: Env): Promise<Response> {
        if (request.method !== 'POST') {
            return new Response('Method not allowed', { status: 405 });
        }

        try {
            const payload = await request.json<any>();

            if (payload.action !== 'created' || !payload.comment.body.includes('/articlecheck')) {
                return new Response('No action taken', { status: 200 });
            }

            await env.MY_QUEUE.send(payload);

            return new Response('Payload sent to queue for processing', { status: 200 });
        } catch (error) {
            console.error('Error processing request:', error);
            if (error instanceof Error) {
                return new Response('Error processing request: ' + error.message, { status: 500 });
            } else {
                return new Response('Unknown error occurred', { status: 500 });
            }
        }
    },

    async queue(batch: MessageBatch<QueueMessage>, env: Env, ctx: ExecutionContext) {
        for (const message of batch.messages) {
            try {
                const prUrl = message.body.issue.pull_request.diff_url;
                const diff = await fetchDiffText(prUrl, env.TOKEN_GITHUB);

                const additions = extractAdditionsFromDiff(diff);
                const extractedStatements = await callLLM(extractingPrompt, `<text>${additions}</text>`, env.LLM_API_KEY, env.LLM_ENDPOINT);

                let searchQueries = await callLLM(retrievingPrompt, extractedStatements, env.LLM_API_KEY, env.LLM_ENDPOINT, env.LLM_MODEL);
                searchQueries = JSON.parse(searchQueries);

                let searchResults = "";

                for (const query of searchQueries) {
                    let result = await webSearch(query, env.BRAVE_API_KEY, env.SEARCH_ENDPOINT);
                    if (result.error || !result.web || !result.web.results) {
                        throw new Error('Search query failed or returned no results');
                    }
                    const formattedSearchResults = formatResultsFull(result.web.results);
                    searchResults += formattedSearchResults;
                    // Add 1-second delay between Brave API calls
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }

                const finalAnswer = await callLLM(
                    answerPrompt,
                    `<statements>${JSON.stringify(extractedStatements)}</statements><fact_checking_results>${searchResults}</fact_checking_results><text>${additions}</text>`,
                    env.LLM_API_KEY,
                    env.LLM_ENDPOINT,
                    env.LLM_MODEL
                );

                await postGitHubComment(message.body.issue.pull_request.url, finalAnswer, env.TOKEN_GITHUB);
                message.ack();
            } catch (error) {
                console.error('Error processing message:', error);
                message.ack();
            }
        }
    }
};