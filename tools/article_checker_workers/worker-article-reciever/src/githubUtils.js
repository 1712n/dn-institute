export async function fetchDiffText(prDetails) {
    const githubToken = TOKEN_GITHUB; 
    const prUrl = prDetails.diff_url;
  
    const headers = {
      "Authorization": `token ${githubToken}`,
      "Accept": "application/vnd.github.v3.diff" 
    };
  
    try {
      const response = await fetch(prUrl, { headers });
      if (!response.ok) {
        throw new Error(`GitHub API responded with status: ${response.status}`);
      }
      const diffText = await response.text(); 
      return diffText;
    } catch (error) {
      console.error('Failed to fetch PR diff:', error);
      return null; 
    }
  }
  
export function extractAdditionsFromDiff(diff) {
    const additionLinesRegex = /^\+(?!\+\+ ).*$/gm;
    const additions = diff.match(additionLinesRegex);
    const cleanAdditions = additions ? additions.map(line => line.substring(1)).join(' ') : '';
    return cleanAdditions;
  }