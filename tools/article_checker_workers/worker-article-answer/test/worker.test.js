import { expect, test, vi } from 'vitest';
import worker from '../src/worker.js';
import { callOpenAI } from '../src/llmUtils.js';

global.TOKEN_GITHUB = 'fake-github-token';
global.OPENAI_API_KEY = 'fake-openai-key';
global.LLM_ENDPOINT = 'https://api.openai.com/v1/chat/completions';
global.LLM_MODEL = 'gpt-3.5-turbo-0125';

vi.mock('../src/llmUtils.js', () => ({
  callOpenAI: vi.fn(),
}));

global.fetch = vi.fn();

test('queue processes messages and posts GitHub comment', async () => {
  const batch = {
    messages: [
      {
        body: {
          completions: '<search_results>Mocked formatted results</search_results>',
          statements: "<statement>the first</statement>\n<statement>the second</statement>",
          diffText: 'added line another added line',
          pullUrl: 'https://api.github.com/repos/test/test/pulls/1'
        }
      }
    ]
  };

  const env = {
    checkerPrompts: new Map([
      ['ANSWER_PROMPT', 'Generate a final answer based on the provided information.']
    ]),
    TOKEN_GITHUB: global.TOKEN_GITHUB,
    OPENAI_API_KEY: global.OPENAI_API_KEY,
    LLM_ENDPOINT: global.LLM_ENDPOINT,
    LLM_MODEL: global.LLM_MODEL
  };

  const openAIResponse = {
    choices: [
      {
        message: {
          content: 'This is the final answer based on the provided information.'
        }
      }
    ]
  };

  callOpenAI.mockResolvedValue(openAIResponse);
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ html_url: 'https://github.com/comment-url' }),
  });

  await worker.queue(batch, env, {});

  expect(callOpenAI).toHaveBeenCalledWith(
    'Generate a final answer based on the provided information.',
    `<statements>${batch.messages[0].body.statements}</statements><fact_checking_results>${batch.messages[0].body.completions}</fact_checking_results><text>${batch.messages[0].body.diffText}</text>`,
    global.OPENAI_API_KEY,
    global.LLM_ENDPOINT,
    global.LLM_MODEL
  );

  expect(fetch).toHaveBeenCalledWith(
    'https://api.github.com/repos/test/test/issues/1/comments',
    {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${global.TOKEN_GITHUB}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
      },
      body: JSON.stringify({ body: 'This is the final answer based on the provided information.' }),
    }
  );
});