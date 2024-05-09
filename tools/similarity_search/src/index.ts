import { Hono } from 'hono';

type Env = {
  AI: {
    run: (modelName: string, inputs: any) => Promise<any>;
  };
  API_KEY_TOKEN_CHECK: string;
  VECTORIZE_INDEX: {
    query: (vectorData: any, options: { namespace: string; topK: number }) => Promise<{ matches: { score: number }[] }>;
  };
};

type TextEntry = {
  text: string;
  namespace: string;
};

const app = new Hono<{ Bindings: Env }>();

app.use('*', async (c, next) => {
  const apiKeyHeader = c.req.header('X-API-Key');
  if (apiKeyHeader !== c.env.API_KEY_TOKEN_CHECK) {
    return c.text('Unauthorized', 401);
  }
  await next();
});

app.post('/', async (c) => {
  const data = await c.req.json<TextEntry>();
  const { text, namespace } = data;

  if (typeof text !== 'string' || typeof namespace !== 'string') {
    return c.text('Invalid JSON format', 400);
  }

  const modelResp = await c.env.AI.run('@cf/baai/bge-base-en-v1.5', { text: [text] });
  const vector = modelResp.data[0];
  const searchResponse = await c.env.VECTORIZE_INDEX.query(vector, { namespace, topK: 1 });
  const similarityScore = searchResponse.matches[0]?.score || 0;

  return c.json({ similarity_score: similarityScore });
});

export default app;