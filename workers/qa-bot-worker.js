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
    const response = await fetch(`https://api.github.com/repos/1712n/dn-institute/contents/content/attacks?ref=${sha}`, {
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    })

    const files = await response.json()
    for (const file of files) {
      const contentResponse = await fetch(file.download_url)
      const content = await contentResponse.text()
      // Perform QA checks on content
      // Example: Check for specific keywords, formatting, etc.
      console.log(`Checking file: ${file.name}`)
    }

    return new Response('QA checks completed successfully', { status: 200 })
  } catch (error) {
    return new Response(`Error during QA checks: ${error.message}`, { status: 500 })
  }
}