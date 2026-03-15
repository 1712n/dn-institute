addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const { headers } = request
  const contentType = headers.get('content-type')

  if (contentType !== 'application/json') {
    return new Response('Invalid content type', { status: 400 })
  }

  const body = await request.json()
  const { pull_request } = body

  if (!pull_request) {
    return new Response('Invalid payload', { status: 400 })
  }

  const response = await fetch(pull_request.diff_url)
  const diff = await response.text()

  const qualityCheckResult = await checkArticleQuality(diff)

  if (qualityCheckResult) {
    await commentOnPullRequest(pull_request.comments_url, qualityCheckResult)
  }

  return new Response('Quality check completed', { status: 200 })
}

async function checkArticleQuality(diff) {
  // Placeholder for actual quality check logic
  // This should call an API or perform checks on the diff content
  return 'Quality check result'
}

async function commentOnPullRequest(commentsUrl, comment) {
  const response = await fetch(commentsUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `token ${CLAUDE_API_KEY}`,
    },
    body: JSON.stringify({ body: comment }),
  })

  if (!response.ok) {
    throw new Error('Failed to comment on pull request')
  }
}
