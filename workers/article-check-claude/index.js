addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Parse the request body
  const body = await request.json();

  // Check if the request is a pull request event
  if (body.action === 'opened' || body.action === 'edited') {
    const prNumber = body.number;
    const repoName = body.repository.name;
    const owner = body.repository.owner.login;

    // Fetch the pull request details
    const prDetails = await fetch(`https://api.github.com/repos/${owner}/${repoName}/pulls/${prNumber}`, {
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });

    const prData = await prDetails.json();
    const articleContent = prData.body; // Assuming the article content is in the PR body

    // Perform article check (dummy check for demonstration)
    const isValid = await checkArticle(articleContent);

    // Comment on the pull request with the result
    await commentOnPR(owner, repoName, prNumber, isValid);

    return new Response('Article check completed', { status: 200 });
  }

  return new Response('Not a pull request event', { status: 200 });
}

async function checkArticle(content) {
  // Dummy article check logic
  return content.length > 100;
}

async function commentOnPR(owner, repoName, prNumber, isValid) {
  const comment = isValid ? 'Article meets the guidelines.' : 'Article does not meet the guidelines.';
  await fetch(`https://api.github.com/repos/${owner}/${repoName}/issues/${prNumber}/comments`, {
    method: 'POST',
    headers: {
      'Authorization': `token ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ body: comment })
  });
}