// 🌰 GitHub API utilities
export async function postGitHubComment(commentsUrl, body, env) {
  const response = await fetch(commentsUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ body }),
  });

  if (!response.ok) {
    throw new Error(`Failed to post comment: ${response.status}`);
  }

  const result = await response.json();
  console.log('🌰 Posted comment:', result.html_url);
  return result;
}