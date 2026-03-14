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

  const files = await fetch(pull_request.files_url)
  const filesData = await files.json()

  for (const file of filesData) {
    if (file.filename.startsWith('content/attacks/')) {
      const fileContent = await fetch(file.raw_url)
      const content = await fileContent.text()

      // Placeholder for QA logic
      const isQuality = await checkArticleQuality(content)

      if (!isQuality) {
        return new Response(`Quality check failed for ${file.filename}`, { status: 400 })
      }
    }
  }

  return new Response('All articles passed quality check', { status: 200 })
}

async function checkArticleQuality(content) {
  // Implement your QA logic here
  // For example, check for specific keywords, length, etc.
  return content.includes('TODO') ? false : true
}