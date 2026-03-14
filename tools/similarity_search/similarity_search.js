import { Vectorize } from 'cloudflare:vectorize';

export async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
    return new Response('Bad Request', { status: 400 });
  }

  if (!data.message) {
    return new Response('Bad Request', { status: 400 });
  }

  try {
    const vectorize = new Vectorize('your-namespace', 'your-collection');
    const results = await vectorize.query(data.message);