export async function fetchDiffText(prDetails, githubToken) {
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
    
    const fileNameRegex = /diff --git a\/(.+?) b\//;
    const fileNameMatch = diff.match(fileNameRegex);
    const fileName = fileNameMatch ? fileNameMatch[1] : 'unknown-file';

    return `${fileName}\n${cleanAdditions}`;
}

export async function postGitHubComment(pullUrl, comment, githubToken) {
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