import { callOpenAI } from "./llmUtils.js";

async function postGitHubComment(pullUrl, comment, githubToken) {
  const issueUrl = pullUrl.replace('/pulls/', '/issues/');
  const url = `${issueUrl}/comments`;

  const headers = {
    "Authorization": `Bearer ${githubToken}`,
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ body: comment }),
    });

    if (!response.ok) {
      throw new Error(`GitHub API responded with status: ${response.status}`);
    }

    const data = await response.json()
    console.log(`Comment posted successfully: ${data.html_url}`);
  } catch (error) {
    console.error('Failed to post comment to GitHub:', error);
  }
}

export default {
  async queue(batch, env, ctx) {
    for (const message of batch.messages) {
      const { completions, statements, diffText, pullUrl } = message.body;
      const answerPrompt = await env.checkerPrompts.get("ANSWER_PROMPT");
      const finalAnswer = await callOpenAI(
        answerPrompt,
        `<statements>${statements}</statements><fact_checking_results>${completions}</fact_checking_results><text>${diffText}</text>`,
        env.OPENAI_API_KEY,
        env.LLM_ENDPOINT,
        env.LLM_MODEL
      );
      const cleanAnswer = finalAnswer.choices[0].message.content;
      const githubToken = env.TOKEN_GITHUB; 
      await postGitHubComment(pullUrl, cleanAnswer, githubToken);
      return new Response({ status: 200 });
    }
  },
};