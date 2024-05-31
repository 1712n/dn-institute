import { TaskProcessor } from "./taskProcessor.js";

export { TaskProcessor };

export default {
  async fetch(request, env, ctx) {
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    const response = new Response("Request received, processing in background", { status: 200 });

    const payload = await request.json();
    const eventId = request.headers.get('X-GitHub-Delivery');
    const prDetails = payload.issue.pull_request;
    const prId = prDetails.url;
    const durableObjectId = env.DURABLE_OBJECT_NAMESPACE.idFromName(prId);
    const durableObjectStub = env.DURABLE_OBJECT_NAMESPACE.get(durableObjectId);

    await durableObjectStub.fetch('http://dummy/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-GitHub-Delivery': eventId },
      body: JSON.stringify({ payload }),
    }).catch(error => console.error("Error in Durable Object fetch:", error));

    return response;
  }
};