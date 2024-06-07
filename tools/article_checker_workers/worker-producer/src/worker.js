addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  console.log(`Received request with method: ${request.method}`);
  
  if (request.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const payload = await request.json();
    const commentBody = payload.comment.body;

    if (payload.action === 'created' && commentBody.includes("/articlecheck")) {
      await MY_QUEUE.send(payload);
      return new Response("Processed by Worker Receiver", { status: 200 });
    } else {
      return new Response("No action taken", { status: 200 });
    }
  } catch (error) {
    console.error('Error processing request:', error);
    return new Response(error.message, { status: 500 });
  }
}