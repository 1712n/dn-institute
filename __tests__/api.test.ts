import { POST } from '../app/api/generate/route';

// Mock the OpenAI client so we don't hit the real API in our test suites
jest.mock('openai', () => {
  return jest.fn().mockImplementation(() => {
    return {
      chat: {
        completions: {
          create: jest.fn().mockResolvedValue({
            choices: [
              {
                message: {
                  content: 'A solar flare flipped a bit in the authentication matrix, causing a temporary cascade failure in the login state sync process.',
                },
              },
            ],
          }),
        },
      },
    };
  });
});

describe('/api/generate API Route', () => {
  it('returns 400 Bad Request if issue payload is missing', async () => {
    const req = new Request('http://localhost/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}), // Missing issue property
    });

    const response = await POST(req);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBe('Issue is required');
  });

  it('returns a successful excuse result and 200 OK status on a valid payload', async () => {
    const req = new Request('http://localhost/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ issue: 'The login page is slow' }),
    });

    const response = await POST(req);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.result).toBe('A solar flare flipped a bit in the authentication matrix, causing a temporary cascade failure in the login state sync process.');
  });
});