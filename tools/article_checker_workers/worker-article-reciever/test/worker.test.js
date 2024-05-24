import { expect, test, vi } from 'vitest';
import { handleRequest } from '../../worker-article-reciever/src/worker.js'; 

global.TOKEN_GITHUB = 'fake-github-token'; 
global.OPENAI_API_KEY = 'fake-openai-key';
global.LLM_ENDPOINT = 'https://api.openai.com/v1/engines/davinci-codex/completions';
global.LLM_MODEL = 'gpt-3.5-turbo-0125';
global.checkerPrompts = new Map([
  ['EXTRACTING_PROMPT', 'Extract statements from the following text'],
  ['RETRIEVAL_PROMPT', 'Formulate queries based on these statements']
]);
global.MY_QUEUE = {
  send: vi.fn(async (data) => {
    const parsedData = JSON.parse(data);
    expect(parsedData).toEqual({
      diffText: 'added line another added line',
      statements: "<statement>the first</statement>\n<statement>the second</statement>",
      retrieveAnswer: [
        { q: "the first", count: 3 },
        { q: "the second", count: 3 }
      ],
      pullUrl: 'https://api.github.com/repos/test/test/pulls/1'
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
          url: 'https://api.github.com/repos/test/test/pulls/1',
          diff_url: 'https://api.github.com/repos/test/test/pulls/1.diff'
        }
      }
    })
  };

  let callCount = 0;
  global.fetch = vi.fn((url, options) => {
    if (url === 'https://api.github.com/repos/test/test/pulls/1.diff') {
      return Promise.resolve({
        ok: true,
        text: () => Promise.resolve('diff --git a/file.txt b/file.txt\n+added line\n+another added line')
      });
    } else if (url === global.LLM_ENDPOINT) {
      if (callCount === 0) {
        callCount++;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            choices: [{ message: { content: "<statement>the first</statement>\n<statement>the second</statement>" } }]
          })
        });
      } else {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            choices: [{ message: { content: JSON.stringify([
              { q: "the first", count: 3 },
              { q: "the second", count: 3 }
            ]) } }]
          })
        });
      }
    } else {
      return Promise.reject(new Error('Unknown URL'));
    }
  });

  const request = new Request('http://localhost', requestPayload);
  const response = await handleRequest(request);
  expect(response.status).toBe(200);
  const responseText = await response.text();
  expect(responseText).toBe('Processed by Worker A');
});