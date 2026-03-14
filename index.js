// Import necessary modules
const GitHubModels = require('github-models');

// Initialize GitHub Models
const ghModels = new GitHubModels();

// Define your AI product logic
async function runAIProduct() {
  try {
    const response = await ghModels.generateText({
      prompt: "Generate a weekly intelligence brief of cyberattacks.",
      maxTokens: 500
    });
    console.log(response);
  } catch (error) {
    console.error("Error generating AI content:", error);
  }
}

// Run the AI product
runAIProduct();