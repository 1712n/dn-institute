import { expect, test, vi } from 'vitest';
import { webSearch, formatResultsFull } from './src/search.js';

const mockSearchResults = {
  web: {
    results: [
      {
        title: "Penguins can't fly",
        url: "https://example.com/penguins",
        description: "Penguins are birds that can't fly over 100 miles."
      },
      {
        title: "Water boiling point",
        url: "https://example.com/water-boiling",
        description: "Water boils at 100 degrees Celsius at sea level."
      }
    ]
  }
};

global.fetch = vi.fn((url, options) => {
  return Promise.resolve({
    ok: true,
    json: async () => mockSearchResults,
  });
});

test('webSearch fetches search results correctly', async () => {
  const params = { q: "Do penguins fly?", count: 3 };
  const BRAVE_API_KEY = 'fake-brave-api-key';
  const SEARCH_ENDPOINT = 'https://api.search.brave.com/api/search';

  const results = await webSearch(params, BRAVE_API_KEY, SEARCH_ENDPOINT);

  expect(global.fetch).toHaveBeenCalledWith(
    expect.any(URL),
    expect.objectContaining({
      headers: expect.objectContaining({
        "X-Subscription-Token": BRAVE_API_KEY
      })
    })
  );
  expect(results).toEqual(mockSearchResults);
});

test('webSearch handles fetch errors correctly', async () => {
  global.fetch.mockImplementationOnce(() => Promise.resolve({
    ok: false,
    status: 404,
    statusText: 'Not Found'
  }));

  const params = { q: "Do penguins fly?", count: 3 };
  const BRAVE_API_KEY = 'fake-brave-api-key';
  const SEARCH_ENDPOINT = 'https://api.search.brave.com/api/search';

  const results = await webSearch(params, BRAVE_API_KEY, SEARCH_ENDPOINT);

  expect(results).toEqual({
    error: true,
    statusCode: 404,
    message: 'Failed to fetch: Not Found'
  });
});

test('formatResultsFull formats search results correctly', () => {
  const formattedResults = formatResultsFull(mockSearchResults.web.results);

  const expectedResults = `<search_results>
<item index="1">
<page_content>
Web Page Title: Penguins can't fly
Web Page URL: https://example.com/penguins
Web Page Summary: <summary>- Penguins are birds that can't fly over 100 miles.
</summary>
</page_content>
</item>
<item index="2">
<page_content>
Web Page Title: Water boiling point
Web Page URL: https://example.com/water-boiling
Web Page Summary: <summary>- Water boils at 100 degrees Celsius at sea level.
</summary>
</page_content>
</item>
</search_results>`;

  expect(formattedResults).toBe(expectedResults);
});