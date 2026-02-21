import { Hono } from "hono";
import { Octokit } from "@octokit/core";
import { Anthropic } from "@anthropic-ai/sdk";
import { BraveSearchClient } from "./search";
import { ArticleChecker } from "./checker";

interface Env {
  GITHUB_TOKEN: string;
  ANTHROPIC_API_KEY: string;
  BRAVE_SEARCH_API_KEY: string;
  GITHUB_APP_ID: string;
}

const app = new Hono<{ Bindings: Env }>();

app.post("/webhook", async (c) => {
  const event = c.req.header("x-github-event");
  const payload = await c.req.json();

  if (event !== "issue_comment") {
    return c.text("Ignored event", 200);
  }

  const comment = payload.comment;
  const issue = payload.issue;
  const repo = payload.repository;

  // 1. Check if comment triggers the bot
  if (!comment.body.includes("/articlecheck") || !issue.pull_request) {
    return c.text("Ignored comment", 200);
  }

  // 2. Setup Clients
  const octokit = new Octokit({ auth: c.env.GITHUB_TOKEN });
  const anthropic = new Anthropic({ apiKey: c.env.ANTHROPIC_API_KEY });
  const brave = new BraveSearchClient(c.env.BRAVE_SEARCH_API_KEY);

  // 3. Post "Checking..." status
  await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
    owner: repo.owner.login,
    repo: repo.name,
    issue_number: issue.number,
    body: "🌰 Checking your article for chestnut quality... Please wait! 🌰",
  });

  try {
    // 4. Run Checker Logic
    const checker = new ArticleChecker(
      octokit,
      brave,
      anthropic,
      repo.owner.login,
      repo.name,
      issue.number
    );

    const result = await checker.run();

    // 5. Post Result
    await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
      owner: repo.owner.login,
      repo: repo.name,
      issue_number: issue.number,
      body: result.markdown_report,
    });

    return c.text("Success", 200);

  } catch (error: any) {
    console.error("Worker Error:", error);
    await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
      owner: repo.owner.login,
      repo: repo.name,
      issue_number: issue.number,
      body: `🌰 Oops! Something cracked. Error: ${error.message}`,
    });
    return c.text("Error", 500);
  }
});

app.get("/", (c) => c.text("🌰 Article Checker Bot is alive!"));

export default app;
