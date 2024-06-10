import { expect, test, vi } from 'vitest';
import { postGitHubComment } from './src/gitHubUtils.js';

global.fetch = vi.fn((url, options) => {
  const urlString = url instanceof URL ? url.href : url;
  if (urlString.endsWith('/issues/1/comments')) {
    return Promise.resolve({
      ok: true,
      json: async () => ({ html_url: 'https://github.com/comment-url' }),
    });
  }
  return Promise.reject(new Error('Unknown URL'));
});

test('postGitHubComment forms the correct URL and posts a comment successfully', async () => {
  const pullUrl = 'https://api.github.com/repos/test/test/pulls/1';
  const comment = 'This is a test comment';
  const githubToken = 'fake-github-token';
  const expectedUrl = 'https://api.github.com/repos/test/test/issues/1/comments';

  await postGitHubComment(pullUrl, comment, githubToken);

  expect(global.fetch).toHaveBeenCalledWith(
    expectedUrl,
    expect.objectContaining({
      method: 'POST',
      headers: expect.objectContaining({
        "Authorization": `Bearer ${githubToken}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
      }),
      body: JSON.stringify({ body: comment }),
    })
  );
});

test('postGitHubComment handles fetch errors correctly and forms the correct URL', async () => {
  global.fetch.mockImplementationOnce(() => Promise.resolve({
    ok: false,
    status: 404,
    statusText: 'Not Found'
  }));

  const pullUrl = 'https://api.github.com/repos/test/test/pulls/1';
  const comment = 'This is a test comment';
  const githubToken = 'fake-github-token';
  const expectedUrl = 'https://api.github.com/repos/test/test/issues/1/comments';

  await postGitHubComment(pullUrl, comment, githubToken);

  expect(global.fetch).toHaveBeenCalledWith(
    expectedUrl,
    expect.objectContaining({
      method: 'POST',
      headers: expect.objectContaining({
        "Authorization": `Bearer ${githubToken}`,
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
      }),
      body: JSON.stringify({ body: comment }),
    })
  );
});