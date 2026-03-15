addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 })
  }

  const payload = await request.json()
  const { pull_request } = payload

  if (!pull_request) {
    return new Response('Invalid payload', { status: 400 })
  }

  const repoOwner = pull_request.head.repo.owner.login
  const repoName = pull_request.head.repo.name
  const prNumber = pull_request.number

  const files = await fetchFiles(repoOwner, repoName, prNumber)

  const results = await Promise.all(files.map(async file => {
    const content = await fetchFileContent(file.raw_url)
    return checkArticle(content)
  }))

  const summary = results.join('\n')

  // Here you would typically send the results back to the PR or a logging service
  console.log(summary)

  return new Response(summary, { status: 200 })
}

async function fetchFiles(owner, repo, prNumber) {
  const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/files`)
  return await response.json()
}

async function fetchFileContent(url) {
  const response = await fetch(url)
  return await response.text()
}

function checkArticle(content) {
  // Implement your article checking logic here
  // For example, check for specific keywords, formatting, etc.
  return `Article checked: ${content.length} characters`
}