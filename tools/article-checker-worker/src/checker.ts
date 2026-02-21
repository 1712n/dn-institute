export interface DiffFile {
  filename: string;
  status: string;
  patch?: string;
}

export interface VerificationResult {
  passed: boolean;
  markdown_report: string;
}

export class ArticleChecker {
  private octokit: any;
  private brave: any;
  private anthropic: any;
  private owner: string;
  private repo: string;
  private prNumber: number;

  constructor(octokit: any, braveClient: any, anthropicClient: any, owner: string, repo: string, prNumber: number) {
    this.octokit = octokit;
    this.brave = braveClient;
    this.anthropic = anthropicClient;
    this.owner = owner;
    this.repo = repo;
    this.prNumber = prNumber;
  }

  async run(): Promise<VerificationResult> {
    // 1. Fetch PR Diff
    const { data: files } = await this.octokit.request("GET /repos/{owner}/{repo}/pulls/{pull_number}/files", {
      owner: this.owner,
      repo: this.repo,
      pull_number: this.prNumber,
    });

    const relevantFiles = files.filter((f: any) => f.filename.endsWith(".md"));
    if (relevantFiles.length === 0) {
      return { passed: true, markdown_report: "🌰 No markdown files found in this PR to check." };
    }

    let report = "## 🌰 Chestnut Quality Check Report\n\n";
    let passed = true;

    for (const file of relevantFiles) {
      const content = file.patch || "No patch content available (new file?)";
      const filename = file.filename;

      report += `### Checking: \`${filename}\`\n`;
      
      // Step 2: Generate Search Queries (Haiku)
      const queryPrompt = `
      You are a fact-checking assistant. Extract 3 specific search queries to verify the facts in this text snippet.
      Return ONLY a JSON array of strings, e.g., ["query 1", "query 2"].
      Text:
      ${content.substring(0, 1500)} // Truncate for efficiency
      `;
      
      const queryResponse = await this.anthropic.messages.create({
        model: "claude-3-haiku-20240307",
        max_tokens: 100,
        messages: [{ role: "user", content: queryPrompt }],
      });
      
      let queries: string[] = [];
      try {
        const jsonText = queryResponse.content[0].text;
        queries = JSON.parse(jsonText.match(/\[.*\]/s)?.[0] || "[]");
      } catch (e) {
        console.error("Failed to parse queries", e);
        queries = [content.substring(0, 50)]; // Fallback
      }

      // Step 3: Execute Search (Brave)
      let searchContext = "";
      for (const q of queries) {
        const results = await this.brave.search(q, 2);
        searchContext += `Query: ${q}\nResults:\n${results.map((r: any) => `- ${r.title}: ${r.description}`).join("\n")}\n\n`;
      }

      // Step 4: Verify Content (Opus)
      const verifyPrompt = `
      You are a strict editor for the "Crypto Attacks Wiki". Verify this article content against the provided search results.
      
      **Rules:**
      1. Check for factual accuracy (dates, amounts, names).
      2. Check for spelling/grammar.
      3. Ensure submission guidelines:
         - Neutral tone (no hype).
         - Clear structure.
         - References if possible.
      4. Use chestnut emojis 🌰 freely in your feedback.
      
      **Input:**
      Article Content:
      ${content}
      
      Search Context:
      ${searchContext}
      
      **Output:**
      - Start with a summary: "✅ Approved" or "❌ Changes Requested".
      - List specific issues with line references if possible.
      - Be helpful and encouraging!
      `;

      const verifyResponse = await this.anthropic.messages.create({
        model: "claude-3-opus-20240229",
        max_tokens: 1000,
        messages: [{ role: "user", content: verifyPrompt }],
      });

      report += verifyResponse.content[0].text + "\n\n---\n";
      
      if (verifyResponse.content[0].text.includes("❌")) {
        passed = false;
      }
    }
    
    return { passed, markdown_report: report };
  }
}
