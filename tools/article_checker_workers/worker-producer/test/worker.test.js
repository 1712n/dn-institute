import { expect, test, vi } from 'vitest';
import { handleRequest } from './src/worker.js'; 

global.MY_QUEUE = {
  send: vi.fn(async (data) => {
    expect(data).toEqual({
      action: 'created',
      comment: {
        body: '/articlecheck'
      },
      issue: {
        pull_request: {
          url: 'https://api.github.com/repos/test/test/pulls/1'
        }
      }
    });
  })
};

test('handleRequest processes a valid webhook event', async () => {
  const requestPayload = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      action: 'created',
      comment: {
        body: '/articlecheck'
      },
      issue: {
        pull_request: {
          url: 'https://api.github.com/repos/test/test/pulls/1'
        }
      }
    })
  };

  const request = new Request('http://localhost', requestPayload);
  const response = await handleRequest(request);
  expect(response.status).toBe(200);
  const responseText = await response.text();
  expect(responseText).toBe('Processed by Worker Receiver');
});

test('handleRequest returns "Method not allowed" for non-POST requests', async () => {
  const requestPayload = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  };

  const request = new Request('http://localhost', requestPayload);
  const response = await handleRequest(request);
  expect(response.status).toBe(405);
  const responseText = await response.text();
  expect(responseText).toBe('Method not allowed');
});

test('handleRequest returns "It is not a relevant comment or action." for irrelevant comments', async () => {
  const requestPayload = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      action: 'created',
      comment: {
        body: 'not relevant'
      },
      issue: {
        pull_request: {
          url: 'https://api.github.com/repos/test/test/pulls/1'
        }
      }
    })
  };

  const request = new Request('http://localhost', requestPayload);
  const response = await handleRequest(request);
  expect(response.status).toBe(200);
  const responseText = await response.text();
  expect(responseText).toBe('It is not a relevant comment or action.');
});

test('handleRequest handles JSON parsing errors', async () => {
  const requestPayload = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: 'invalid json'
  };

  const request = new Request('http://localhost', requestPayload);
  const response = await handleRequest(request);
  expect(response.status).toBe(500);
  const responseText = await response.text();
  expect(responseText).toMatch(/Unexpected token/);
});