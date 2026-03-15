addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const { headers } = request
  const contentType = headers.get('content-type')

  if (contentType && contentType.includes('application/json')) {
    const body = await request.json()
    const result = await checkArticle(body)
    return new Response(JSON.stringify(result), { status: 200, headers: { 'Content-Type': 'application/json' } })
  } else {
    return new Response('Invalid request format', { status: 400 })
  }
}

async function checkArticle(data) {
  // Placeholder for article checking logic
  // This should be replaced with actual logic to check the article
  const { pull_request } = data
  const articleUrl = pull_request.head.repo.html_url + '/blob/' + pull_request.head.ref + '/' + pull_request.head.label.split(':')[1].trim()

  // Example check: Ensure the article URL is valid
  const isValidUrl = articleUrl.startsWith('https://github.com/')

  return {
    isValid: isValidUrl,
    message: isValidUrl ? 'Article URL is valid' : 'Article URL is invalid'
  }
}