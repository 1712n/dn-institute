import { json } from 'worktop/response';

const VECTORIZE_API_URL = 'https://api.cloudflare.com/client/v4/accounts/{account_id}/vectorize/v1/namespaces/{namespace}/query';

export async function handleRequest(request) {
  if (request.method !== 'POST') return json({ error: 'Method not allowed' }, 405);

  try {
    const body = await request.json();
    if (!body || typeof body.message !== 'string') {
    }

    const response = await fetch(VECTORIZE_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.CLOUDFLARE_API_TOKEN}`
      body: JSON.stringify({ queries: [{ vector: [0.1, 0.2, 0.3], topK: 2 }] })
    });

    const { matches } = await response.json();
    return json({ matches });
  } catch (error) {
    return json({ error: 'Internal server error' }, 500);
  } catch (error) {
  }
}