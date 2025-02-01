export const config = {
  // Cohere Configuration
  COHERE_MODEL: 'command',
  COHERE_TEMPERATURE: 0.0,
  COHERE_MAX_TOKENS: 4000,
  
  // Search Configuration
  SEARCH_MAX_RESULTS: 5,
  SEARCH_TIMEOUT: 60000,
  
  // Article Processing
  MAX_TOKENS_TO_READ: 20000,
  SUMMARIZE_THRESHOLD: 0.7,
  
  // Retry Configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,
  
  // Endpoints
  BRAVE_SEARCH_ENDPOINT: 'https://api.search.brave.com/res/v1/web/search',
  
  // Prompts
  EXTRACTING_PROMPT: `
    Please extract important statements that appear to be factual from the text provided.
    Return the extracted statements. Place each statement within <statement></statement> tags.
    Also, return the number of extracted statements within <number_of_statements></number_of_statements> tags.
    Aim to extract important statements with numbers, dates, and names of organizations.
    There should not be too many extracted statements.
    Skip the preamble; go straight into the result.
  `,
  
  VERIFICATION_PROMPT: `
    Verify the following statement using the provided search results:
    Statement: {statement}
    
    Search Results:
    {searchResults}
    
    Respond with a JSON object containing:
    - isFactual (boolean): whether the statement is supported by the evidence
    - explanation (string): explanation of the verification
    - source (string): URL of the most relevant source, or "None" if no supporting evidence
  `,
  
  DUPLICATION_PROMPT: `
    Compare the following article with existing content to check for duplication.
    New Article:
    {newArticle}
    
    Existing Article:
    {existingArticle}
    
    Respond with a JSON object containing:
    - isDuplicate (boolean): whether the articles contain substantially similar content
    - similarity (number): similarity score between 0 and 1
    - explanation (string): explanation of the similarity assessment
  `
} as const; 