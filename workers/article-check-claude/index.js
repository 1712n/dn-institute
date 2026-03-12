addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const { headers } = request
  const contentType = headers.get('content-type')

  if (contentType && contentType.includes('application/json')) {
    const body = await request.json()
    const isValid = await checkArticle(body)
    return new Response(JSON.stringify({ isValid }), {
      headers: { 'Content-Type': 'application/json' },
      status: isValid ? 200 : 400
    })
  }

  return new Response('Invalid request format', { status: 400 })
}

async function checkArticle(data) {
  // Simulate article check logic
  // Replace with actual logic to validate article
  const { title, content } = data
  if (!title || !content) {
    return false
  }
  // Example: Check if title is at least 10 characters long and content is at least 100 characters long
  return title.length >= 10 && content.length >= 100
}