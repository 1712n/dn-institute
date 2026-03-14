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

  const { head } = pull_request
  const { sha } = head

  try {
    const result = await checkArticle(sha)
    return new Response(JSON.stringify(result), { status: 200, headers: { 'Content-Type': 'application/json' } })
  } catch (error) {
    return new Response(error.message, { status: 500 })
  }
}

async function checkArticle(sha) {
  // Simulate article check logic
  // This should be replaced with actual logic to fetch the PR content and perform checks
  const response = await fetch(`https://api.github.com/repos/1712n/dn-institute/contents/content/attacks?ref=${sha}`)
  const files = await response.json()

  const results = files.map(file => ({
    name: file.name,
    status: 'checked', // This should be determined by the actual check logic
    message: 'Article meets guidelines' // This should be determined by the actual check logic
  }))

  return { results }
}